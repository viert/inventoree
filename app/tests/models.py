from app.models import Datacenter as BaseDatacenter
from app.models import Project as BaseProject
from app.models import Group as BaseGroup
from app.models import Host as BaseHost
from app.models import User as BaseUser


class TestDatacenter(BaseDatacenter):
    _collection = "test_datacenter"


class TestProject(BaseProject):
    _collection = "test_project"


class TestGroup(BaseGroup):
    _collection = "test_group"


class TestHost(BaseHost):
    _collection = "test_host"


class TestUser(BaseUser):
    _collection = "test_user"


# cross-links avoiding, that"s why need explicit setattr
# TestProject <-> TestGroup
#
setattr(TestProject, "_owner_class", TestUser)
setattr(TestProject, "_group_class", TestGroup)
setattr(TestGroup, "_project_class", TestProject)
setattr(TestGroup, "_host_class", TestHost)
setattr(TestHost, "_group_class", TestGroup)
setattr(TestHost, "_datacenter_class", TestDatacenter)