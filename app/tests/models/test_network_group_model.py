from unittest import TestCase
from app.models import WorkGroup, User, NetworkGroup, Host
from library.engine.errors import FieldRequired, InvalidWorkGroupId, ServerGroupNotEmpty


class TestNetworkGroupModel(TestCase):

    @classmethod
    def setUpClass(cls):
        WorkGroup.destroy_all()
        WorkGroup.ensure_indexes()
        cls.twork_group_owner = User(username='test_user', password_hash='test_hash', supervisor=False, system=False)
        cls.twork_group_owner.save()
        cls.system_user = User(username='test_system_user', password_hash='test_hash', supervisor=False, system=True)
        cls.system_user.save()
        cls.twork_group = WorkGroup(name="test_work_group", owner_id=cls.twork_group_owner._id)
        cls.twork_group.save()
        cls.twork_group2 = WorkGroup(name="test_work_group2", owner_id=cls.twork_group_owner._id)
        cls.twork_group2.save()

    def setUp(self):
        NetworkGroup.destroy_all()

    def tearDown(self):
        NetworkGroup.destroy_all()

    @classmethod
    def tearDownClass(cls):
        NetworkGroup.destroy_all()
        WorkGroup.destroy_all()
        User.destroy_all()

    def test_incomplete(self):
        sg = NetworkGroup()
        self.assertRaises(FieldRequired, sg.save)
        sg.name = "my test group"
        sg.work_group_id = "some invalid id"
        self.assertRaises(InvalidWorkGroupId, sg.save)

    def test_permissions(self):
        sg = NetworkGroup(name='ng1', work_group_id=self.twork_group._id)
        sg.save()
        self.assertFalse(sg._modification_allowed_by(self.twork_group_owner))
        self.assertTrue(sg._modification_allowed_by(self.system_user))

    def test_get(self):
        sg = NetworkGroup(name='ng1', work_group_id=self.twork_group._id)
        sg.save()
        sg = NetworkGroup.get("ng1")
        self.assertIsNotNone(sg)

    def test_destroy_not_empty(self):
        sg = NetworkGroup(name='ng1', work_group_id=self.twork_group._id)
        sg.save()
        host = Host(fqdn='host.example.com', network_group_id=sg._id)
        host.save()
        self.assertRaises(ServerGroupNotEmpty, sg.destroy)
        host.destroy()
        sg.destroy()
