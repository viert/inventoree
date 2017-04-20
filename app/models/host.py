from storable_model import StorableModel, InvalidTags, now


class InvalidGroup(Exception):
    pass


class InvalidDatacenter(Exception):
    pass


class Host(StorableModel):

    _group_class = None
    _datacenter_class = None

    FIELDS = (
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
        "short_name",
        "group_id",
    )

    REJECTED_FIELDS = (
        "created_at",
        "updated_at",
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
        if not hasattr(self.tags, "__getitem__"):
            raise InvalidTags("Tags must be of array type")
        self.touch()

    @property
    def group(self):
        return self._group_class.find_one({ "_id": self.group_id })

    @property
    def datacenter(self):
        return self._datacenter_class.find_one({ "_id": self.datacenter_id })

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
