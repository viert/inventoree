from httpapi_testcase import HttpApiTestCase
from app.models import ServerGroup


class TestServerGroupCtrl(HttpApiTestCase):

    @classmethod
    def setUpClass(cls):
        HttpApiTestCase.setUpClass()
        ServerGroup.ensure_indexes()

    def setUp(self):
        ServerGroup.destroy_all()
        self.sg1 = ServerGroup(name="sg1", work_group_id=self.work_group1._id)
        self.sg1.save()
        self.sg2 = ServerGroup(name="sg2", work_group_id=self.work_group2._id)
        self.sg2.save()
        self.sg3 = ServerGroup(name="sg3", work_group_id=self.work_group1._id)
        self.sg3.save()

    def tearDown(self):
        ServerGroup.destroy_all()

    def test_list_server_groups(self):
        data = self.get_json_data_should_be_successful("/api/v1/server_groups/")
        self.assertEqual(3, data["count"])

        data = self.get_json_data_should_be_successful("/api/v1/server_groups/?work_group_id=%s" % self.work_group1._id)
        self.assertEqual(2, data["count"])

        data = self.get_json_data_should_be_successful("/api/v1/server_groups/?work_group_name=%s" % self.work_group2.name)
        self.assertEqual(1, data["count"])

        data = self.get_json_data_should_be_successful("/api/v1/server_groups/%s" % self.sg1.name)
        self.assertEqual(1, data["count"])
        sg = data["data"][0]
        self.assertEqual(str(self.sg1._id), sg["_id"])
        self.assertEqual(str(self.sg1.work_group_id), sg["work_group_id"])
        self.assertEqual(self.sg1.is_master, sg["is_master"])
        self.assertEqual(self.sg1.name, sg["name"])

    def test_create_server_group_insuff_perms(self):
        payload = {
            "name": "sg4",
            "work_group_name": self.work_group1.name
        }
        r = self.post_json("/api/v1/server_groups/", payload, supervisor=True, system=False)
        self.assertEqual(403, r.status_code, "non system user should have no permissions to create SGs")

    def test_create_server_group(self):
        payload = {
            "name": "sg4",
            "work_group_name": self.work_group1.name
        }
        r = self.post_json("/api/v1/server_groups/", payload, supervisor=False, system=True)
        self.assertEqual(201, r.status_code)
        sg = ServerGroup.get("sg4")
        self.assertIsNotNone(sg)

    def test_create_server_group_invalid_wg(self):
        payload = {
            "name": "sg4",
            "work_group_name": "non-existing"
        }
        r = self.post_json("/api/v1/server_groups/", payload, supervisor=False, system=True)
        self.assertEqual(404, r.status_code)

