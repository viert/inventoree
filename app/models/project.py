from app.models.storable_model import StorableModel, now


class ProjectNotEmpty(Exception):
    pass


class InvalidOwner(Exception):
    pass

class Project(StorableModel):

    _owner_class = None
    _group_class = None

    FIELDS = (
        '_id',
        'name',
        'description',
        'email',
        'root_email',
        'owner_id',
        'updated_at',
        'created_at',
    )

    REQUIRED_FIELDS = (
        'name',
        'created_at',
        'updated_at',
        'owner_id',
    )

    DEFAULTS = {
        "created_at": now,
        "updated_at": now
    }

    REJECTED_FIELDS = (
        'created_at',
        'updated_at',
        'owner_id'
    )

    INDEXES = [
        [ "name", { "unique": True } ]
    ]

    __slots__ = FIELDS

    @property
    def owner_class(self):
        if self._owner_class is None:
            from app.models import User
            self.__class__._owner_class = User
        return self._owner_class

    @property
    def owner(self):
        return self.owner_class.find_one({ "_id": self.owner_id })

    @property
    def owner_name(self):
        return self.owner.username

    @property
    def group_class(self):
        if self._group_class is None:
            from app.models import Group
            self.__class__._group_class = Group
        return self._group_class

    def _before_save(self):
        if not self.is_new:
            self.touch()
        if self.owner is None:
            raise InvalidOwner("Can't find user by project's owner_id")

    def touch(self):
        self.updated_at = now()

    def _before_delete(self):
        if self.groups.count() > 0:
            raise ProjectNotEmpty("Can not delete project having groups")

    @property
    def groups(self):
        return self.group_class.find({ "project_id": self._id })