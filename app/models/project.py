from app.models.storable_model import StorableModel, now


class ProjectNotEmpty(Exception):
    pass


class Project(StorableModel):
    FIELDS = (
        '_id',
        'name',
        'description',
        'email',
        'root_email',
        'created_at',
        'updated_at',
    )

    REQUIRED_FIELDS = (
        'name',
        'created_at',
        'updated_at',
    )

    DEFAULTS = {
        "created_at": now,
        "updated_at": now
    }

    INDEXES = [
        [ "name", { "unique": True } ]
    ]

    __slots__ = FIELDS

    def _before_save(self):
        if not self.is_new:
            self.touch()

    def touch(self):
        self.updated_at = now()

    def _before_delete(self):
        if self.groups.count() > 0:
            raise ProjectNotEmpty("Can not delete project having groups")

    @property
    def groups(self):
        from app.models import Group
        return Group.find({ "project_id": self._id })