from storable_model import StorableModel, now

class Host(StorableModel):

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
        "updated_at": now
    }

    INDEXES = (
        "fqdn",
        "short_name",
        ["group_id", "datacenter_id"],
        "datacenter_id",
        "tags",
    )

    __slots__ = FIELDS