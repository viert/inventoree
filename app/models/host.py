from storable_model import StorableModel, now
from library.engine.errors import InvalidTags, InvalidCustomFields, DatacenterNotFound, GroupNotFound
from library.engine.utils import get_user_from_app_context


class Host(StorableModel):

    _group_class = None
    _datacenter_class = None

    FIELDS = (
        "_id",
        "fqdn",
        "group_id",
        "datacenter_id",
        "description",
        "tags",
        "custom_fields",
        "created_at",
        "updated_at",
    )

    KEY_FIELD = "fqdn"

    REQUIRED_FIELDS = (
        "fqdn",
    )

    REJECTED_FIELDS = (
        "created_at",
        "updated_at",
    )

    DEFAULTS = {
        "created_at": now,
        "updated_at": now,
        "tags": [],
        "custom_fields": []
    }

    INDEXES = (
        [ "fqdn", { "unique": True } ],
        "group_id",
        "datacenter_id",
        "tags",
        [ "custom_fields.key", "custom_fields.value" ]
    )

    __slots__ = FIELDS

    def touch(self):
        self.updated_at = now()


    def __hash__(self):
        return hash(self.fqdn + "." + str(self._id))

    def _before_save(self):
        if self.group_id is not None and self.group is None:
            raise GroupNotFound("Can not find group with id %s" % self.group_id)
        if self.datacenter_id is not None and self.datacenter is None:
            raise DatacenterNotFound("Can not find datacenter with id %s" % self.datacenter_id)
        if not hasattr(self.tags, "__getitem__") or type(self.tags) is str:
            raise InvalidTags("Tags must be of array type")

        # Custom fields validation
        if type(self.custom_fields) is not list:
            raise InvalidCustomFields("Custom fields must be of array type")
        custom_keys = set()
        for cf in self.custom_fields:
            if type(cf) is not dict:
                raise InvalidCustomFields("Custom field must be a dict")
            if "key" not in cf or "value" not in cf:
                raise InvalidCustomFields("Custom field must contain key and value fields")
            else:
                if cf["key"].strip() == "":
                    raise InvalidCustomFields("Custom field key can't be empty")
                if cf["value"].strip() == "":
                    raise InvalidCustomFields("Custom field value can't be empty")
                if cf["key"] in custom_keys:
                    raise InvalidCustomFields("Key '%s' is provided more than once" % cf["key"])
                else:
                    custom_keys.add(cf["key"])

        self.touch()

    @property
    def group(self):
        return self.group_class.find_one({ "_id": self.group_id })

    @property
    def group_name(self):
        if self.group is None:
            return ""
        return self.group.name

    @property
    def datacenter(self):
        return self.datacenter_class.find_one({ "_id": self.datacenter_id })

    @property
    def location(self):
        return self.datacenter()

    @property
    def datacenter_name(self):
        dc = self.datacenter
        if dc is None:
            return None
        else:
            return dc.name

    @property
    def location_name(self):
        return self.datacenter_name()

    @property
    def root_datacenter(self):
        dc = self.datacenter_class.find_one({ "_id": self.datacenter_id })
        if dc is None:
            return None
        elif dc.root_id is None:
            return dc
        else:
            return self.datacenter_class.find_one({ "_id": dc.root_id })

    @property
    def root_location(self):
        return self.root_datacenter()

    @property
    def root_datacenter_name(self):
        rdc = self.root_datacenter
        if rdc is None:
            return None
        else:
            return rdc.name

    @property
    def root_location_name(self):
        return self.root_datacenter_name()

    @property
    def group_class(self):
        if self._group_class is None:
            from app.models import Group
            self.__class__._group_class = Group
        return self._group_class

    @property
    def location_class(self):
        return self.datacenter_class()

    @property
    def datacenter_class(self):
        if self._datacenter_class is None:
            from app.models import Datacenter
            self.__class__._datacenter_class = Datacenter
        return self._datacenter_class

    @property
    def modification_allowed(self):
        if self.group is None:
            return True
        return self.group.modification_allowed

    @property
    def destruction_allowed(self):
        if self.group is None:
            user = get_user_from_app_context()
            if user is not None and user.supervisor:
                return True
            else:
                return False
        return self.group.modification_allowed

    @property
    def all_tags(self):
        tags = set(self.tags)
        if self.is_new or self.group is None:
            return tags
        return tags.union(self.group.all_tags)

    @property
    def all_custom_fields(self):
        # the handler may be a bit heavy, be sure to benchmark it
        if self.is_new or self.group is None:
            return self.custom_fields

        cf_dict = {}
        for cf in self.group.all_custom_fields:
            cf_dict[cf["key"]] = cf["value"]
        for cf in self.custom_fields:
            cf_dict[cf["key"]] = cf["value"]
        custom_fields = []
        for k,v in cf_dict.items():
            custom_fields.append({ "key": k, "value": v })

        return custom_fields

    @classmethod
    def unset_datacenter(cls, datacenter_id):
        from library.db import db
        db.conn[cls.collection].update_many({ "datacenter_id": datacenter_id }, { "$set": { "datacenter_id": None }})

    @classmethod
    def unset_location(cls, location_id):
        cls.unset_datacenter(location_id)