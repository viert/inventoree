import re
from storable_model import StorableModel, now
from library.engine.errors import InvalidTags, InvalidCustomFields, DatacenterNotFound, \
                                GroupNotFound, InvalidAliases, InvalidFQDN, InvalidIpAddresses
from library.engine.utils import get_user_from_app_context
from library.engine.cache import request_time_cache

FQDN_EXPR = re.compile('^[_a-z0-9\-.]+$')
ANSIBLE_CF_PREFIX = "ansible:"

class Host(StorableModel):

    _group_class = None
    _datacenter_class = None

    FIELDS = (
        "_id",
        "fqdn",
        "group_id",
        "datacenter_id",
        "description",
        "aliases",
        "tags",
        "custom_fields",
        "created_at",
        "updated_at",
        "ip_addrs"
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
        "custom_fields": [],
        "aliases": [],
        "ip_addrs": []
    }

    INDEXES = (
        [ "fqdn", { "unique": True } ],
        "group_id",
        "datacenter_id",
        "tags",
        "aliases",
        [ "custom_fields.key", "custom_fields.value" ]
    )

    SYSTEM_FIELDS = (
        "ip_addrs",
    )

    __slots__ = FIELDS

    def touch(self):
        self.updated_at = now()

    def __hash__(self):
        return hash(self.fqdn + "." + str(self._id))

    def _before_save(self):
        if not FQDN_EXPR.match(self.fqdn):
            raise InvalidFQDN("FQDN %s is invalid" % self.fqdn)
        if self.group_id is not None and self.group is None:
            raise GroupNotFound("Can not find group with id %s" % self.group_id)
        if self.datacenter_id is not None and self.datacenter is None:
            raise DatacenterNotFound("Can not find datacenter with id %s" % self.datacenter_id)
        if not hasattr(self.tags, "__getitem__") or type(self.tags) is str:
            raise InvalidTags("Tags must be of array type")
        if len(set(self.tags)) != len(self.tags):
            raise InvalidTags("Tags must be unique")
        if not hasattr(self.ip_addrs, "__getitem__") or type(self.ip_addrs) is str:
            raise InvalidIpAddresses("Ip addresses must be of array type")
        if not hasattr(self.aliases, "__getitem__") or type(self.aliases) is str:
            raise InvalidAliases("Aliases must be of array type")

        # Custom fields validation
        if type(self.custom_fields) is not list:
            raise InvalidCustomFields("Custom fields must be of array type")
        custom_keys = set()
        for cf in self.custom_fields:
            if type(cf) is not dict:
                raise InvalidCustomFields("Every custom field item must be a dict")
            if "key" not in cf or "value" not in cf:
                raise InvalidCustomFields("Every custom field item must contain key and value fields")
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
        if self.group_id is None:
            return None
        return self.group_class.find_one({ "_id": self.group_id })

    @property
    def group_name(self):
        if self.group is None:
            return ""
        return self.group.name

    @property
    @request_time_cache()
    def work_group(self):
        if self.group is None:
            return None
        return self.group.work_group

    @property
    def work_group_name(self):
        work_group = self.work_group
        if work_group is None:
            return None
        return work_group.name

    @property
    def responsibles(self):
        work_group = self.work_group
        if work_group is None:
            return None
        return work_group.participants

    @property
    def datacenter(self):
        if self.datacenter_id is None:
            return None
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
    def system_modification_allowed(self):
        from library.engine.utils import can_assign_system_fields
        return can_assign_system_fields()

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
    @request_time_cache()
    def all_tags(self):
        tags = set(self.tags)
        if self.is_new or self.group is None:
            return tags
        return tags.union(self.group.all_tags)

    @property
    @request_time_cache()
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

    @property
    def ansible_vars(self):
        cfs = self.all_custom_fields
        vars = {}
        cut = len(ANSIBLE_CF_PREFIX)
        for cf in cfs:
            if cf["key"].startswith(ANSIBLE_CF_PREFIX):
                vars[cf["key"][cut:]] = cf["value"]
        return vars

    def set_custom_field(self, key, value):
        i = -1
        for (ind, cf) in enumerate(self.custom_fields):
            if cf["key"] == key:
                i = ind
                break
        if i < 0:
            self.custom_fields.append({"key": key, "value": value})
        else:
            self.custom_fields[i]["value"] = value

    def remove_custom_field(self, key):
        i = -1
        for (ind, cf) in enumerate(self.custom_fields):
            if cf["key"] == key:
                i = ind
                break
        if i < 0:
            return

        self.custom_fields = self.custom_fields[:i] + self.custom_fields[i+1:]

    @classmethod
    def unset_datacenter(cls, datacenter_id):
        from library.db import db
        db.conn[cls.collection].update_many({ "datacenter_id": datacenter_id }, { "$set": { "datacenter_id": None }})

    @classmethod
    def unset_location(cls, location_id):
        cls.unset_datacenter(location_id)

    def add_tag(self, tag):
        if tag in self.tags:
            return
        self.tags.append(tag)

    def remove_tag(self, tag):
        if tag not in self.tags:
            return
        self.tags.remove(tag)