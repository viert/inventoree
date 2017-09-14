from httpapi_testcase import HttpApiTestCase
from flask import json
from app.models import Host
from bson.objectid import ObjectId

TEST_HOST_1 = {
    "fqdn": "host1.example.com",
    "description": "test host 1",
    "tags": ["boo", "meow", "roar"]
}

TEST_HOST_2 = {
    "fqdn": "host2.example.com",
    "description": "test host 2",
    "tags": ["smm", "pm", "dev"]
}

class TestHostCtrl(HttpApiTestCase):

    def setUp(self):
        Host.destroy_all()

    def test_create_host(self):
        payload = TEST_HOST_1
        r = self.post_json("/api/v1/hosts/", payload)
        self.assertEqual(r.status_code, 201)
        data = json.loads(r.data)
        self.assertIn("data", data)

        host_data = data["data"]
        self.assertIs(type(host_data), list)
        self.assertEqual(len(host_data), 1)

        host = host_data[0]
        self.assertIn("_id", host)
        host = Host.find_one({"_id": ObjectId(host["_id"])})
        self.assertIsNotNone(host)
        self.assertEqual(payload["fqdn"], host.fqdn)
        self.assertEqual(payload["description"], host.description)
        self.assertItemsEqual(payload["tags"], host.tags)

    def test_show_host(self):
        h = Host(**TEST_HOST_1)
        h.save()
        r = self.get("/api/v1/hosts/%s" % h._id)
        self.assertEqual(200, r.status_code)
        data = json.loads(r.data)
        self.assertIn("data", data)
        data = data["data"]
        self.assertIs(list, type(data))
        self.assertEqual(1, len(data))
        host_attrs = data[0]
        self.assertEqual(h.fqdn, host_attrs["fqdn"])
        self.assertItemsEqual(h.tags, host_attrs["tags"])
        self.assertEqual(h.description, host_attrs["description"])

    def test_update_host(self):
        self.test_create_host()
        host = Host.find_one({ "fqdn": TEST_HOST_1["fqdn"] })
        payload = TEST_HOST_2
        r = self.put_json("/api/v1/hosts/%s" % host._id, payload)
        self.assertEqual(r.status_code, 200)
        host = Host.find_one({ "_id": host._id })
        self.assertEqual(host.fqdn, TEST_HOST_2["fqdn"])
        self.assertEqual(host.description, TEST_HOST_2["description"])
        self.assertItemsEqual(host.tags, TEST_HOST_2["tags"])

    def test_delete_host(self):
        self.test_create_host()
        host = Host.find_one({ "fqdn": TEST_HOST_1["fqdn"] })
        r = self.delete("/api/v1/hosts/%s" % host._id)
        self.assertEqual(r.status_code, 200)
        data = json.loads(r.data)
        self.assertIn("data", data)
        host_data = data["data"]
        self.assertEqual(host_data["_id"], None)
        host = Host.find_one({"_id": host._id})
        self.assertIsNone(host)

    def test_mass_delete(self):
        from app.models import Group
        g1 = Group(name="g1", project_id=self.project1._id)
        g1.save()
        h1 = Host(fqdn="host1", group_id=g1._id)
        h1.save()
        h2 = Host(fqdn="host2", group_id=g1._id)
        h2.save()
        h3 = Host(fqdn="host3", group_id=g1._id)
        h3.save()
        h4 = Host(fqdn="host4", group_id=g1._id)
        h4.save()
        r = self.post_json("/api/v1/hosts/mass_delete", { "host_ids": [str(h2._id), str(h3._id)]})
        self.assertEqual(200, r.status_code)
        data = json.loads(r.data)
        self.assertIn("data", data)
        hosts_data = data["data"]
        self.assertIn("hosts", hosts_data)
        hosts_data = hosts_data["hosts"]
        self.assertIs(list, type(hosts_data))
        self.assertEqual(2, len(hosts_data))
        deleted_hosts = Host.find({"_id":{"$in":[h2._id, h3._id]}})
        self.assertEqual(0, deleted_hosts.count())
        g1 = Group.find_one({"_id": g1._id})
        self.assertItemsEqual([h1._id, h4._id], g1.host_ids)

    def test_mass_move(self):
        from app.models import Group
        g1 = Group(name="g1", project_id=self.project1._id)
        g1.save()
        g2 = Group(name="g2", project_id=self.project1._id)
        g2.save()
        h1 = Host(fqdn="host1", group_id=g1._id)
        h1.save()
        h2 = Host(fqdn="host2", group_id=g1._id)
        h2.save()
        h3 = Host(fqdn="host3", group_id=g1._id)
        h3.save()
        h4 = Host(fqdn="host4", group_id=g1._id)
        h4.save()
        r = self.post_json("/api/v1/hosts/mass_move",
                           { "host_ids": [str(h2._id), str(h3._id)], "group_id": str(g2._id)})
        self.assertEqual(200, r.status_code)
        data = json.loads(r.data)
        self.assertIn("data", data)
        hosts_data = data["data"]
        self.assertIn("hosts", hosts_data)
        hosts_data = hosts_data["hosts"]
        self.assertIs(list, type(hosts_data))
        self.assertEqual(2, len(hosts_data))
        g1 = Group.find_one({"_id": g1._id})
        g2 = Group.find_one({"_id": g2._id})
        self.assertItemsEqual([h1._id, h4._id], g1.host_ids)
        self.assertItemsEqual([h2._id, h3._id], g2.host_ids)