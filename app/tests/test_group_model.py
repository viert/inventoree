from unittest import TestCase
from app.models import Group as BaseGroup
from app.models import User as BaseUser
from app.models import Project as BaseProject
from app.models.storable_model import FieldRequired, ParentCycle, ChildAlreadyExists, ParentAlreadyExists

class TestUser(BaseUser):
    _collection = 'test_user'


class TestProject(BaseProject):
    _owner_class = TestUser
    _collection = "test_project"


class TestGroup(BaseGroup):
    _collection = "test_group"
    _project_class = TestProject


class TestGroupModel(TestCase):

    @classmethod
    def setUpClass(cls):
        TestProject.destroy_all()
        TestGroup.destroy_all()
        TestProject.ensure_indexes()
        TestGroup.ensure_indexes()
        cls.tproject_owner = TestUser(username='viert', password_hash='hash')
        cls.tproject_owner.save()
        cls.tproject = TestProject(name="test_project", owner_id=cls.tproject_owner._id)
        cls.tproject.save()
        cls.tproject2 = TestProject(name="test_project2", owner_id=cls.tproject_owner._id)
        cls.tproject2.save()

    def setUp(self):
        TestGroup.destroy_all()

    def tearDown(self):
        TestGroup.destroy_all()

    @classmethod
    def tearDownClass(cls):
        TestGroup.destroy_all()
        TestProject.destroy_all()
        TestUser.destroy_all()

    def test_incomplete(self):
        from app.models.group import InvalidProjectId
        group = TestGroup()
        self.assertRaises(FieldRequired, group.save)
        group.name = "my test group"
        group.project_id = "some invalid id"
        self.assertRaises(InvalidProjectId, group.save)

    def test_children_before_save(self):
        from app.models.storable_model import ObjectSaveRequired
        g1 = TestGroup(name="g1")
        g2 = TestGroup(name="g2")
        self.assertRaises(ObjectSaveRequired, g1.add_child, g2)
        self.assertRaises(ObjectSaveRequired, g2.add_parent, g1)

    def test_self_parent(self):
        g1 = TestGroup(name="g1", project_id=self.tproject._id)
        g1.save()
        self.assertRaises(ParentCycle, g1.add_parent, g1)

    def test_self_child(self):
        g1 = TestGroup(name="g1", project_id=self.tproject._id)
        g1.save()
        self.assertRaises(ParentCycle, g1.add_child, g1)

    def test_child_already_exists(self):
        g1 = TestGroup(name="g1", project_id=self.tproject._id)
        g1.save()
        g2 = TestGroup(name="g2", project_id=self.tproject._id)
        g2.save()
        g1.add_child(g2)
        self.assertRaises(ChildAlreadyExists, g1.add_child, g2)

    def test_parent_already_exists(self):
        g1 = TestGroup(name="g1", project_id=self.tproject._id)
        g1.save()
        g2 = TestGroup(name="g2", project_id=self.tproject._id)
        g2.save()
        g1.add_parent(g2)
        self.assertRaises(ParentAlreadyExists, g1.add_parent, g2)

    def test_cycle(self):
        g1 = TestGroup(name="g1", project_id=self.tproject._id)
        g1.save()
        g2 = TestGroup(name="g2", project_id=self.tproject._id)
        g2.save()
        g3 = TestGroup(name="g3", project_id=self.tproject._id)
        g3.save()
        g4 = TestGroup(name="g4", project_id=self.tproject._id)
        g4.save()
        g1.add_child(g2)
        g2.add_child(g3)
        g3.add_child(g4)
        self.assertRaises(ParentCycle, g4.add_child, g1)
        self.assertRaises(ParentCycle, g1.add_parent, g4)

    def test_add_child_via_attrs(self):
        g1 = TestGroup(name="g1", project_id=self.tproject._id)
        g1.save()
        g2 = TestGroup(name="g2", project_id=self.tproject._id)
        g2.save()

        g1.add_child(g2)
        tg = TestGroup.find_one({ "name": "g1" })
        self.assertIn(g2._id, tg.child_ids)
        g1.remove_child(g2)

        g1.add_child(g2._id)
        tg = TestGroup.find_one({ "name": "g1" })
        self.assertIn(g2._id, tg.child_ids)
        g1.remove_child(g2._id)

        g1.add_child(str(g2._id))
        tg = TestGroup.find_one({ "name": "g1" })
        self.assertIn(g2._id, tg.child_ids)
        g1.remove_child(str(g2._id))

    def test_add_child_with_different_project(self):
        from app.models.group import InvalidProjectId
        g1 = TestGroup(name="g1", project_id=self.tproject._id)
        g1.save()
        g2 = TestGroup(name="g2", project_id=self.tproject2._id)
        g2.save()

        self.assertRaises(InvalidProjectId, g1.add_child, g2)
        self.assertRaises(InvalidProjectId, g1.add_parent, g2)