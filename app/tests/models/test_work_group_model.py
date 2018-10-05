from unittest import TestCase
from app.models import WorkGroup, User, Group
from app.models.work_group import WorkGroupNotEmpty, InvalidOwner
from time import sleep
from pymongo.errors import DuplicateKeyError

TEST_PROJECT_NAME = "testCase.my_unique_test_work_group"
TEST_GROUP_NAME = "testCase.my_unique_test_group"


class TestProjectModel(TestCase):

    @classmethod
    def setUpClass(cls):
        WorkGroup.destroy_all()
        WorkGroup.ensure_indexes()
        Group.destroy_all()
        Group.ensure_indexes()
        User.destroy_all()
        User.ensure_indexes()
        cls.owner = User(username='viert', password_hash='hash')
        cls.owner.save()
        WorkGroup.ensure_indexes()

    @classmethod
    def tearDownClass(cls):
        cls.owner.destroy()

    def setUp(self):
        Group.destroy_all()
        p = WorkGroup.find_one({"name": TEST_PROJECT_NAME})
        if p is not None:
            p.destroy()

    def tearDown(self):
        Group.destroy_all()
        p = WorkGroup.find_one({"name": TEST_PROJECT_NAME})
        if p is not None:
            p.destroy()

    def test_unique_index(self):
        p = WorkGroup(name=TEST_PROJECT_NAME, owner_id=self.owner._id)
        p.save()
        p = WorkGroup(name=TEST_PROJECT_NAME, owner_id=self.owner._id)
        self.assertRaises(DuplicateKeyError, p.save)

    def test_touch_on_save(self):
        p = WorkGroup(name=TEST_PROJECT_NAME, owner_id=self.owner._id)
        p.save()
        dt1 = p.updated_at
        sleep(1)
        p.save()
        dt2 = p.updated_at
        self.assertNotEqual(dt1, dt2, msg="updated_at not changed while saving Project")

    def test_delete_non_empty(self):
        p = WorkGroup(name=TEST_PROJECT_NAME, owner_id=self.owner._id)
        p.save()
        g = Group(name=TEST_GROUP_NAME, work_group_id=p._id)
        g.save()
        self.assertRaises(WorkGroupNotEmpty, p.destroy)
        g.destroy()
        p.destroy()

    def test_owner(self):
        p = WorkGroup(name="TEST_PROJECT_NAME", owner_id="arbitrary")
        self.assertRaises(InvalidOwner, p.save)
