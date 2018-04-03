from storable_model import StorableModel, now


class ApiAction(StorableModel):

    FIELDS = (
        "_id",
        "username",
        "action_type",
        "kwargs",
        "params",
        "status",
        "errors",
        "created_at",
        "updated_at",
    )

    REQUIRED_FIELDS = (
        "username",
        "action_type",
        "status",
        "created_at",
        "updated_at",
    )

    DEFAULTS = {
        "kwargs": {},
        "params": {},
        "created_at": now,
        "updated_at": now,
        "errors": []
    }

    REJECTED_FIELDS = (
        "created_at",
        "updated_at",
    )

    INDEXES = (
        "username",
        "action_type",
        "status",
        "created_at",
        "updated_at",
    )

    __slots__ = list(FIELDS)

    def _before_save(self):
        self.updated_at = now()
