from httpapi_testcase import HttpApiTestCase
from flask import json
from app.models import Host
from bson.objectid import ObjectId

TEST_HOST_1 = {
    "fqdn": "host1.example.com",
    "description": "test host 1",
    "tags": ["boo", "meow", "roar"]
}

TEST_HOST_1_SHORT_NAME = "host1"

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
        self.assertEqual(TEST_HOST_1_SHORT_NAME, host.short_name)
        self.assertEqual(payload["description"], host.description)
        self.assertItemsEqual(payload["tags"], host.tags)

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