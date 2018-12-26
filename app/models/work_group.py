from app.models.storable_model import StorableModel, now
from library.engine.permissions import get_user_from_app_context
from library.engine.utils import check_lists_are_equal


class WorkGroupNotEmpty(Exception):
    pass


class InvalidOwner(Exception):
    pass


class WorkGroup(StorableModel):

    _owner_class = None
    _group_class = None

    FIELDS = (
        "_id",
        "name",
        "description",
        "email",
        "owner_id",
        "member_ids",
        "updated_at",
        "created_at",
    )

    KEY_FIELD = "name"

    REQUIRED_FIELDS = (
        "name",
        "created_at",
        "updated_at",
        "owner_id",
        "member_ids"
    )

    DEFAULTS = {
        "created_at": now,
        "updated_at": now,
        "member_ids": [],
        "description": "",
        "email": "",
    }

    REJECTED_FIELDS = (
        "created_at",
        "updated_at",
        "owner_id",
        "member_ids"
    )

    INDEXES = [
        [ "name", { "unique": True } ],
        "member_ids",
        "owner_id"
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
        return self.owner_class.find_one({"_id": self.owner_id})

    @property
    def owner_name(self):
        return self.owner.username

    @property
    def members(self):
        return self.owner_class.find({"_id":{"$in":self.member_ids}})

    @property
    def member_usernames(self):
        return [x.username for x in self.members]

    @property
    def participants(self):
        return self.owner_class.find({
            "_id": {"$in": self.member_ids + [self.owner_id]}
        })

    @property
    def participant_usernames(self):
        return [x.username for x in self.participants]

    @property
    def modification_allowed(self):
        user = get_user_from_app_context()
        if user is None: return False
        if user.supervisor or self.owner._id == user._id: return True
        if user._id in self.member_ids: return True
        return False

    @property
    def member_list_modification_allowed(self):
        user = get_user_from_app_context()
        if user is None: return False
        if user.supervisor or self.owner._id == user._id: return True
        return False

    def is_member(self, user):
        return user._id in self.member_ids

    def add_member(self, user):
        if user._id not in self.member_ids:
            self.member_ids.append(user._id)
        self.save()

    def remove_member(self, user):
        if user._id in self.member_ids:
            self.member_ids.remove(user._id)
        self.save()

    @property
    def group_class(self):
        if self._group_class is None:
            from app.models import Group
            self.__class__._group_class = Group
        return self._group_class

    def _before_save(self):
        if self.owner is None:
            raise InvalidOwner("can not save workgroup without an owner")
        if not self.is_new:
            self.touch()
        if self.owner_id != self._initial_state.get("owner_id") or \
                not check_lists_are_equal(self.member_ids, self._initial_state.get("member_ids")):
            self.reset_responsibles_cache()

    def touch(self):
        self.updated_at = now()

    def reset_responsibles_cache(self):
        for group in self.groups:
            group.reset_responsibles_cache(self.participant_usernames)
            group.save(skip_callback=True)

    def _before_delete(self):
        if self.groups_count > 0:
            raise WorkGroupNotEmpty("can not delete workgroup having groups")
        if self.network_groups_count > 0:
            raise WorkGroupNotEmpty("can not delete workgroup having server groups")

    @property
    def groups_count(self):
        return self.groups.count()

    @property
    def groups(self):
        return self.group_class.find({"work_group_id": self._id})

    @property
    def network_groups(self):
        from app.models import NetworkGroup
        return NetworkGroup.find({"work_group_id": self._id})

    @property
    def network_groups_count(self):
        return self.network_groups.count()

    @property
    def hosts(self):
        from app.models import Host
        group_ids = [x._id for x in self.groups]
        return Host.find({"group_id": {"$in": group_ids}})
