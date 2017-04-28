from unittest import TestCase
from app.tests.models.test_models import TestHost, TestGroup, TestDatacenter, TestProject, TestUser
from app.models.host import InvalidGroup, InvalidDatacenter, InvalidTags
from pymongo.errors import DuplicateKeyError

class TestHostModel(TestCase):

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

    @classmethod
    def tearDownClass(cls):
        TestHost.destroy_all()
        TestGroup.destroy_all()
        TestProject.destroy_all()
        TestUser.destroy_all()

    def setUp(self):
        TestHost.destroy_all()
        TestGroup.destroy_all()

    def tearDown(self):
        TestHost.destroy_all()
        TestGroup.destroy_all()

    def test_invalid_group(self):
        g = TestGroup(name="test_group", project_id=self.tproject._id)
        g.save()
        group_id = g._id
        g.destroy()
        h = TestHost(fqdn="host.example.com", group_id=group_id)
        self.assertRaises(InvalidGroup, h.save)

    def test_invalid_datacenter(self):
        g = TestGroup(name="test_group", project_id=self.tproject._id)
        g.save()
        d = TestDatacenter(name="test_datacenter")
        d.save()
        dc_id = d._id
        d.destroy()
        h = TestHost(fqdn="host.example.com", group_id=g._id, datacenter_id=dc_id)
        self.assertRaises(InvalidDatacenter, h.save)

    def test_invalid_tags(self):
        g = TestGroup(name="test_group", project_id=self.tproject._id)
        g.save()
        h = TestHost(fqdn="host.example.com", group_id=g._id, tags="invalid_tags")
        self.assertRaises(InvalidTags, h.save)

    def test_short_name(self):
        g = TestGroup(name="test_group", project_id=self.tproject._id)
        g.save()

        h = TestHost(fqdn="host.example.com", group_id=g._id)
        h.save()
        self.assertEqual(h.short_name, "host")

        h = TestHost(fqdn="host.subdomain.example.com", group_id=g._id)
        h.save()
        self.assertEqual(h.short_name, "host.subdomain")

        h = TestHost(fqdn="host.example", group_id=g._id)
        h.save()
        self.assertEqual(h.short_name, "host.example")

        h = TestHost(fqdn="host2", group_id=g._id)
        h.save()
        self.assertEqual(h.short_name, "host2")

    def test_duplicate_fqdn(self):
        g = TestGroup(name="test_group", project_id=self.tproject._id)
        g.save()
        h = TestHost(fqdn="host.example.com", group_id=g._id)
        h.save()
        h = TestHost(fqdn="host.example.com", group_id=g._id)
        self.assertRaises(DuplicateKeyError, h.save)

    def test_duplicate_short_name(self):
        g = TestGroup(name="test_group", project_id=self.tproject._id)
        g.save()
        h = TestHost(fqdn="host.example.com", group_id=g._id)
        h.save()
        h = TestHost(fqdn="host.example2.info", group_id=g._id)
        self.assertRaises(DuplicateKeyError, h.save)

    def test_root_datacenter(self):
        g = TestGroup(name="test_group", project_id=self.tproject._id)
        g.save()
        dc1 = TestDatacenter(name="dc1")
        dc1.save()
        dc11 = TestDatacenter(name="dc1.1")
        dc11.save()
        dc11.set_parent(dc1)
        h = TestHost(fqdn="host.example.com", group_id=g._id, datacenter_id=dc11._id)
        h.save()
        self.assertEqual(h.root_datacenter, dc1)