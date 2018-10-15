from unittest import TestCase
from app.models import WorkGroup, User, ServerGroup
from library.engine.errors import FieldRequired, InvalidWorkGroupId


class TestServerGroupModel(TestCase):

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
        ServerGroup.destroy_all()

    def tearDown(self):
        ServerGroup.destroy_all()

    @classmethod
    def tearDownClass(cls):
        ServerGroup.destroy_all()
        WorkGroup.destroy_all()
        User.destroy_all()

    def test_incomplete(self):
        sg = ServerGroup()
        self.assertRaises(FieldRequired, sg.save)
        sg.name = "my test group"
        sg.work_group_id = "some invalid id"
        self.assertRaises(InvalidWorkGroupId, sg.save)

    def test_permissions(self):
        sg = ServerGroup(name='sg1', work_group_id=self.twork_group._id)
        sg.save()
        self.assertFalse(sg._modification_allowed_by(self.twork_group_owner))
        self.assertTrue(sg._modification_allowed_by(self.system_user))

    def test_get(self):
        sg = ServerGroup(name='sg1', work_group_id=self.twork_group._id)
        sg.save()
        sg = ServerGroup.get("sg1")
        self.assertIsNotNone(sg)
