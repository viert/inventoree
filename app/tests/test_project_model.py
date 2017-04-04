from unittest import TestCase
from app.models import Project
from time import sleep
from pymongo.errors import DuplicateKeyError

TEST_PROJECT_NAME = "testCase.my_unique_test_project"

class TestProjectModel(TestCase):

    def setUp(self):
        p = Project.find_one({ "name": TEST_PROJECT_NAME })
        if p is not None:
            p.destroy()

    def tearDown(self):
        p = Project.find_one({ "name": TEST_PROJECT_NAME })
        if p is not None:
            p.destroy()

    def test_unique_index(self):
        p = Project(name=TEST_PROJECT_NAME)
        p.save()
        p = Project(name=TEST_PROJECT_NAME)
        self.assertRaises(DuplicateKeyError, p.save)

    def test_touch_on_save(self):
        p = Project(name=TEST_PROJECT_NAME)
        p.save()
        dt1 = p.updated_at
        sleep(1)
        p.save()
        dt2 = p.updated_at
        self.assertNotEqual(dt1, dt2, msg="updated_at not changed while saving Project")