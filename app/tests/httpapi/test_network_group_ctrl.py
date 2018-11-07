from httpapi_testcase import HttpApiTestCase
from app.models import NetworkGroup, Host


class TestNetworkGroupCtrl(HttpApiTestCase):

    @classmethod
    def setUpClass(cls):
        HttpApiTestCase.setUpClass()
        NetworkGroup.ensure_indexes()

    def setUp(self):
        NetworkGroup.destroy_all()
        self.sg1 = NetworkGroup(name="sg1", work_group_id=self.work_group1._id)
        self.sg1.save()
        self.sg2 = NetworkGroup(name="sg2", work_group_id=self.work_group2._id)
        self.sg2.save()
        self.sg3 = NetworkGroup(name="sg3", work_group_id=self.work_group1._id)
        self.sg3.save()

    def tearDown(self):
        NetworkGroup.destroy_all()

    def test_list_network_groups(self):
        data = self.get_json_data_should_be_successful("/api/v1/network_groups/")
        self.assertEqual(3, data["count"])

        data = self.get_json_data_should_be_successful("/api/v1/network_groups/?work_group_id=%s" % self.work_group1._id)
        self.assertEqual(2, data["count"])

        data = self.get_json_data_should_be_successful("/api/v1/network_groups/?work_group_name=%s" % self.work_group2.name)
        self.assertEqual(1, data["count"])

        data = self.get_json_data_should_be_successful("/api/v1/network_groups/%s" % self.sg1.name)
        self.assertEqual(1, data["count"])
        sg = data["data"][0]
        self.assertEqual(str(self.sg1._id), sg["_id"])
        self.assertEqual(str(self.sg1.work_group_id), sg["work_group_id"])
        self.assertEqual(self.sg1.is_master, sg["is_master"])
        self.assertEqual(self.sg1.name, sg["name"])

    def test_create_network_group_insuff_perms(self):
        payload = {
            "name": "sg4",
            "work_group_name": self.work_group1.name
        }
        r = self.post_json("/api/v1/network_groups/", payload, supervisor=True, system=False)
        self.assertEqual(403, r.status_code, "non system user should have no permissions to create SGs")

    def test_create_network_group(self):
        payload = {
            "name": "sg4",
            "work_group_name": self.work_group1.name
        }
        r = self.post_json("/api/v1/network_groups/", payload, supervisor=False, system=True)
        self.assertEqual(201, r.status_code)
        sg = NetworkGroup.get("sg4")
        self.assertIsNotNone(sg)

    def test_create_network_group_invalid_wg(self):
        payload = {
            "name": "sg4",
            "work_group_name": "non-existing"
        }
        r = self.post_json("/api/v1/network_groups/", payload, supervisor=False, system=True)
        self.assertEqual(404, r.status_code)

    def test_delete_network_group_insuff_perms(self):
        r = self.delete("/api/v1/network_groups/%s" % self.sg1._id, supervisor=True, system=False)
        self.assertEqual(403, r.status_code)

    def test_delete_network_group_with_hosts(self):
        h = Host(fqdn="host.example.com", network_group_id=self.sg1._id)
        h.save()
        r = self.delete("/api/v1/network_groups/%s" % self.sg1._id, supervisor=False, system=True)
        self.assertEqual(200, r.status_code)
        h.reload()
        self.assertIsNone(h.network_group_id)
