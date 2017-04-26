from unittest import TestCase
from app.tests.models import TestProject, TestGroup, TestHost, TestUser
from app.models.storable_model import FieldRequired, ParentCycle,\
    ChildAlreadyExists, ParentAlreadyExists, InvalidTags


class TestGroupModel(TestCase):

    @classmethod
    def setUpClass(cls):
        TestProject.destroy_all()
        TestProject.ensure_indexes()
        TestGroup.destroy_all()
        TestGroup.ensure_indexes()
        TestHost.destroy_all()
        TestHost.ensure_indexes()
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
        TestHost.destroy_all()

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

    def test_group_hosts(self):
        g1 = TestGroup(name="g1", project_id=self.tproject._id)
        g1.save()
        g2 = TestGroup(name="g2", project_id=self.tproject._id)
        g2.save()
        g1.add_child(g2)

        host1 = TestHost(fqdn="host1.example.com", short_name='host1', group_id=g1._id)
        host1.save()
        host2 = TestHost(fqdn="host2.example.com", short_name='host2', group_id=g2._id)
        host2.save()

        self.assertItemsEqual([host1], g1.hosts)
        self.assertItemsEqual([host2], g2.hosts)
        self.assertItemsEqual([host1, host2], g1.all_hosts)

    def test_tags(self):
        g1 = TestGroup(name="g1", project_id=self.tproject._id, tags=["tag1", "tag2"])
        g1.save()
        g2 = TestGroup(name="g2", project_id=self.tproject._id, tags=["tag2", "tag3"])
        g2.save()
        g1.add_child(g2)
        self.assertItemsEqual(["tag1", "tag2"], g1.all_tags)
        self.assertItemsEqual(["tag1", "tag2", "tag3"], g2.all_tags)
        dictg2 = g2.to_dict(fields=list(TestGroup.FIELDS) + ["all_tags"])
        self.assertItemsEqual(["tag1", "tag2", "tag3"], dictg2["all_tags"])

        # testing tag set JSON encoding
        from app import app
        import flask.json as json
        json.dumps(dictg2, default=app.flask.json_encoder().default)

    def test_invalid_tags(self):
        g1 = TestGroup(name="g1", project_id=self.tproject._id, tags="invalid tags")
        self.assertRaises(InvalidTags, g1.save)

    def test_change_project_id(self):
        from app.models.group import InvalidProjectId
        g1 = TestGroup(name="g1", project_id=self.tproject._id)
        g1.save()
        g2 = TestGroup(name="g2", project_id=self.tproject._id)
        g2.save()

        g1.add_child(g2)
        g2.project_id = self.tproject2._id
        self.assertRaises(InvalidProjectId, g2.save)
        g1.project_id = self.tproject2._id
        self.assertRaises(InvalidProjectId, g1.save)

