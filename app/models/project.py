from app.models.storable_model import StorableModel, now

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
