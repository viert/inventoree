from storable_model import StorableModel
from library.engine.permissions import get_user_from_app_context
from library.engine.errors import InvalidWorkGroupId, ServerGroupNotEmpty


class NetworkGroup(StorableModel):

    # This model relates to mail.ru-specific terms

    _collection = 'network_groups'

    FIELDS = (
        "_id",
        "name",
        "work_group_id",
        "is_master",
    )

    REQUIRED_FIELDS = (
        "work_group_id",
        "name"
    )

    INDEXES = (
        ["name", {"unique": True}],
        "work_group_id",
        "is_master"
    )

    DEFAULTS = {
        "is_master": False
    }

    KEY_FIELD = "name"

    __slots__ = FIELDS

    @property
    def work_group(self):
        from app.models import WorkGroup
        return WorkGroup.find_one({"_id": self.work_group_id})

    @property
    def work_group_name(self):
        wg = self.work_group
        if wg is None:
            return None
        return wg.name

    @property
    def modification_allowed(self):
        user = get_user_from_app_context()
        return self._modification_allowed_by(user)

    @property
    def assigning_allowed(self):
        return self.work_group.modification_allowed

    @property
    def hosts(self):
        from app.models import Host
        return Host.find({"network_group_id": self._id})

    @property
    def hosts_count(self):
        return self.hosts.count()

    def _check_work_group(self):
        if self.work_group is None and self.work_group_id is not None:
            raise InvalidWorkGroupId("WorkGroup with id %s doesn't exist" % self.work_group_id)

    def _before_save(self):
        self._check_work_group()

    def _before_delete(self):
        if self.hosts_count > 0:
            raise ServerGroupNotEmpty("server group has hosts attached")

    def clear_hosts(self):
        for host in self.hosts:
            host.network_group_id = None
            host.save()

    @staticmethod
    def _modification_allowed_by(user):
        if user is None:
            return False
        return user.system
