from unittest import TestCase
from app.models import WorkGroup, Group, Host, User
from library.engine.errors import FieldRequired, ParentCycle, ChildAlreadyExists, ParentAlreadyExists, InvalidTags
from bson.objectid import ObjectId

TEST_CUSTOM_FIELDS_G1 = [
    { "key": "field1", "value": "1" },
    { "key": "field2", "value": "2" }
]
TEST_CUSTOM_FIELDS_G2 = [
    { "key": "field2", "value": "overriden 2" },
    { "key": "field3", "value": "3" }
]
TEST_CUSTOM_FIELDS_RESULT = [
    {"key": "field1", "value": "1"},
    {"key": "field2", "value": "overriden 2"},
    {"key": "field3", "value": "3"}
]

TEST_CUSTOM_FIELDS_RIP_G1 = [
    {"key": "field1", "value": "1"},
    {"key": "field2", "value": "2"}
]
TEST_CUSTOM_FIELDS_RIP_G2 = [
    { "key": "field2", "value": "overriden 2" },
    { "key": "field3", "value": "3" }
]
TEST_CUSTOM_FIELDS_RIP_G3 = [
    { "key": "field4", "value": "4" }
]
TEST_CUSTOM_FIELDS_RIP_RESULT1 = [
    {"key": "field1", "value": "1"},
    {"key": "field2", "value": "overriden 2"},
    {"key": "field3", "value": "3"},
    {"key": "field4", "value": "4"}
]
TEST_CUSTOM_FIELDS_RIP_RESULT2 = [
    {"key": "field1", "value": "1"},
    {"key": "field2", "value": "2"},
    {"key": "field4", "value": "4"}
]


class TestGroupModel(TestCase):

    @classmethod
    def setUpClass(cls):
        WorkGroup.destroy_all()
        WorkGroup.ensure_indexes()
        Group.destroy_all()
        Group.ensure_indexes()
        Host.destroy_all()
        Host.ensure_indexes()
        cls.twork_group_owner = User(username='test_user', password_hash='test_hash')
        cls.twork_group_owner.save()
        cls.twork_group = WorkGroup(name="test_work_group", owner_id=cls.twork_group_owner._id)
        cls.twork_group.save()
        cls.twork_group2 = WorkGroup(name="test_work_group2", owner_id=cls.twork_group_owner._id)
        cls.twork_group2.save()

    def setUp(self):
        Group.destroy_all()

    def tearDown(self):
        Group.destroy_all()

    @classmethod
    def tearDownClass(cls):
        Group.destroy_all()
        WorkGroup.destroy_all()
        User.destroy_all()
        Host.destroy_all()

    def test_incomplete(self):
        from app.models.group import InvalidWorkGroupId
        group = Group()
        self.assertRaises(FieldRequired, group.save)
        group.name = "my test group"
        group.work_group_id = "some invalid id"
        self.assertRaises(InvalidWorkGroupId, group.save)

    def test_children_before_save(self):
        from app.models.storable_model import ObjectSaveRequired
        g1 = Group(name="g1")
        g2 = Group(name="g2")
        self.assertRaises(ObjectSaveRequired, g1.add_child, g2)
        self.assertRaises(ObjectSaveRequired, g2.add_parent, g1)

    def test_self_parent(self):
        g1 = Group(name="g1", work_group_id=self.twork_group._id)
        g1.save()
        self.assertRaises(ParentCycle, g1.add_parent, g1)

    def test_self_child(self):
        g1 = Group(name="g1", work_group_id=self.twork_group._id)
        g1.save()
        self.assertRaises(ParentCycle, g1.add_child, g1)

    def test_child_already_exists(self):
        g1 = Group(name="g1", work_group_id=self.twork_group._id)
        g1.save()
        g2 = Group(name="g2", work_group_id=self.twork_group._id)
        g2.save()
        g1.add_child(g2)
        self.assertRaises(ChildAlreadyExists, g1.add_child, g2)

    def test_parent_already_exists(self):
        g1 = Group(name="g1", work_group_id=self.twork_group._id)
        g1.save()
        g2 = Group(name="g2", work_group_id=self.twork_group._id)
        g2.save()
        g1.add_parent(g2)
        self.assertRaises(ParentAlreadyExists, g1.add_parent, g2)

    def test_cycle(self):
        g1 = Group(name="g1", work_group_id=self.twork_group._id)
        g1.save()
        g2 = Group(name="g2", work_group_id=self.twork_group._id)
        g2.save()
        g3 = Group(name="g3", work_group_id=self.twork_group._id)
        g3.save()
        g4 = Group(name="g4", work_group_id=self.twork_group._id)
        g4.save()
        g1.add_child(g2)
        g2.add_child(g3)
        g3.add_child(g4)
        self.assertRaises(ParentCycle, g4.add_child, g1)
        self.assertRaises(ParentCycle, g1.add_parent, g4)

    def test_add_child_via_attrs(self):
        g1 = Group(name="g1", work_group_id=self.twork_group._id)
        g1.save()
        g2 = Group(name="g2", work_group_id=self.twork_group._id)
        g2.save()

        g1.add_child(g2)
        tg = Group.find_one({ "name": "g1" })
        self.assertIn(g2._id, tg.child_ids)
        g1.remove_child(g2)

        g1.add_child(g2._id)
        tg = Group.find_one({ "name": "g1" })
        self.assertIn(g2._id, tg.child_ids)
        g1.remove_child(g2._id)

        g1.add_child(str(g2._id))
        tg = Group.find_one({ "name": "g1" })
        self.assertIn(g2._id, tg.child_ids)
        g1.remove_child(str(g2._id))

    def test_add_child_with_different_work_group(self):
        from app.models.group import InvalidWorkGroupId
        g1 = Group(name="g1", work_group_id=self.twork_group._id)
        g1.save()
        g2 = Group(name="g2", work_group_id=self.twork_group2._id)
        g2.save()

        self.assertRaises(InvalidWorkGroupId, g1.add_child, g2)
        self.assertRaises(InvalidWorkGroupId, g1.add_parent, g2)

    def test_group_hosts(self):
        g1 = Group(name="g1", work_group_id=self.twork_group._id)
        g1.save()
        g2 = Group(name="g2", work_group_id=self.twork_group._id)
        g2.save()
        g1.add_child(g2)

        host1 = Host(fqdn="host1.example.com", group_id=g1._id)
        host1.save()
        host2 = Host(fqdn="host2.example.com", group_id=g2._id)
        host2.save()

        self.assertItemsEqual([host1], g1.hosts)
        self.assertItemsEqual([host2], g2.hosts)
        self.assertItemsEqual([host1, host2], g1.all_hosts)

    def test_tags(self):
        g1 = Group(name="g1", work_group_id=self.twork_group._id, tags=["tag1", "tag2"])
        g1.save()
        g2 = Group(name="g2", work_group_id=self.twork_group._id, tags=["tag2", "tag3"])
        g2.save()
        g1.add_child(g2)
        self.assertItemsEqual(["tag1", "tag2"], g1.all_tags)
        self.assertItemsEqual(["tag1", "tag2", "tag3"], g2.all_tags)
        dictg2 = g2.to_dict(fields=list(Group.FIELDS) + ["all_tags"])
        self.assertItemsEqual(["tag1", "tag2", "tag3"], dictg2["all_tags"])

        # testing tag set JSON encoding
        from app import app
        import flask.json as json
        json.dumps(dictg2, default=app.flask.json_encoder().default)

    def test_custom_fields(self):
        g1 = Group(name="g1", work_group_id=self.twork_group._id, custom_fields=TEST_CUSTOM_FIELDS_G1)
        g1.save()
        g2 = Group(name="g2", work_group_id=self.twork_group._id, custom_fields=TEST_CUSTOM_FIELDS_G2)
        g2.save()
        g1.add_child(g2)
        self.assertItemsEqual(g2.all_custom_fields, TEST_CUSTOM_FIELDS_RESULT)

    def test_custom_fields_remove_intermediate_parent(self):
        g1 = Group(name="g1", work_group_id=self.twork_group._id, custom_fields=TEST_CUSTOM_FIELDS_RIP_G1)
        g1.save()
        g2 = Group(name="g2", work_group_id=self.twork_group._id, custom_fields=TEST_CUSTOM_FIELDS_RIP_G2)
        g2.save()
        g1.add_child(g2)
        g3 = Group(name="g3", work_group_id=self.twork_group._id, custom_fields=TEST_CUSTOM_FIELDS_RIP_G3)
        g3.save()
        g2.add_child(g3)
        self.assertItemsEqual(g3.all_custom_fields, TEST_CUSTOM_FIELDS_RIP_RESULT1)
        g2.remove_all_children()
        g2.destroy()
        self.assertItemsEqual(g3.all_custom_fields, TEST_CUSTOM_FIELDS_RIP_G3)
        g1.add_child(g3)
        self.assertItemsEqual(g3.all_custom_fields, TEST_CUSTOM_FIELDS_RIP_RESULT2)

    def test_invalid_tags(self):
        g1 = Group(name="g1", work_group_id=self.twork_group._id, tags="invalid tags")
        self.assertRaises(InvalidTags, g1.save)

    def test_change_work_group_id(self):
        from app.models.group import InvalidWorkGroupId
        g1 = Group(name="g1", work_group_id=self.twork_group._id)
        g1.save()
        g2 = Group(name="g2", work_group_id=self.twork_group._id)
        g2.save()

        g1.add_child(g2)
        g2.work_group_id = self.twork_group2._id
        self.assertRaises(InvalidWorkGroupId, g2.save)
        g1.work_group_id = self.twork_group2._id
        self.assertRaises(InvalidWorkGroupId, g1.save)

    def test_remove_deleted_group_refs(self):
        g1 = Group(name="g1", work_group_id=self.twork_group._id)
        g1.save()
        g2 = Group(name="g2", work_group_id=self.twork_group._id)
        g2.save()
        g1.add_child(g2)
        parent_id = g1._id
        g1 = Group.find_one({ "_id": parent_id })
        self.assertItemsEqual([g2], g1.children)
        g2.destroy()
        g1 = Group.find_one({ "_id": parent_id })
        self.assertItemsEqual([], g1.children)

    def test_remove_faulty_child(self):
        g1 = Group(name="g1", work_group_id=self.twork_group._id)
        g1.save()
        ch_id = ObjectId(None)
        g1.child_ids = [ch_id]
        g1.save(skip_callback=True)
        g1 = Group.find_one({ "_id": g1._id })
        self.assertEqual(len(g1.child_ids), 1)
        g1.remove_child(str(ch_id))
        g1 = Group.find_one({ "_id": g1._id })
        self.assertEqual(len(g1.child_ids), 0)

