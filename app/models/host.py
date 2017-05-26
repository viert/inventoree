from storable_model import StorableModel, InvalidTags, now


class InvalidGroup(Exception):
    pass


class InvalidDatacenter(Exception):
    pass


class Host(StorableModel):

    _group_class = None
    _datacenter_class = None

    FIELDS = (
        "_id",
        "fqdn",
        "short_name",
        "group_id",
        "datacenter_id",
        "description",
        "tags",
        "created_at",
        "updated_at",
    )

    REQUIRED_FIELDS = (
        "fqdn",
    )

    REJECTED_FIELDS = (
        "created_at",
        "updated_at",
        "group_id",
    )

    DEFAULTS = {
        "created_at": now,
        "updated_at": now,
        "tags": []
    }

    INDEXES = (
        [ "fqdn", { "unique": True } ],
        [ "short_name", { "unique": True } ],
        "group_id",
        "datacenter_id",
        "tags",
    )

    __slots__ = FIELDS

    def touch(self):
        self.updated_at = now()

    def _before_save(self):
        if self.group_id is not None and self.group is None:
            raise InvalidGroup("Can not find group with id %s" % self.group_id)
        if self.datacenter_id is not None and self.datacenter is None:
            raise InvalidDatacenter("Can not find datacenter with id %s" % self.datacenter_id)
        if not hasattr(self.tags, "__getitem__") or type(self.tags) is str:
            raise InvalidTags("Tags must be of array type")
        if self.short_name is None:
            self._guess_short_name()
        self.touch()

    def _guess_short_name(self):
        short_name_domains = self.fqdn.split(".")[:-2]
        if len(short_name_domains) == 0:
            short_name = self.fqdn
        else:
            short_name = '.'.join(short_name_domains)
        self.short_name = short_name

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
    def datacenter_name(self):
        dc = self.datacenter
        if dc is None:
            return None
        else:
            return dc.name

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
    def root_datacenter_name(self):
        rdc = self.root_datacenter
        if rdc is None:
            return None
        else:
            return rdc.name

    @property
    def group_class(self):
        if self._group_class is None:
            from app.models import Group
            self.__class__._group_class = Group
        return self._group_class

    @property
    def datacenter_class(self):
        if self._datacenter_class is None:
            from app.models import Datacenter
            self.__class__._datacenter_class = Datacenter
        return self._datacenter_class

    @property
    def all_tags(self):
        tags = set(self.tags)
        if self.is_new:
            return tags
        return tags.union(self.group.all_tags)

    @classmethod
    def unset_datacenter(cls, datacenter_id):
        from library.db import db
        db.conn[cls.collection].update_many({ "datacenter_id": datacenter_id }, { "$set": { "datacenter_id": None }})
