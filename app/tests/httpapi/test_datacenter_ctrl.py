from httpapi_testcase import HttpApiTestCase
from flask import json
from app.models import Datacenter
from bson.objectid import ObjectId


class TestDatacenterCtrl(HttpApiTestCase):

    def create_datacenter_tree(self):
        self.dc1 = Datacenter(name="dc1", description="Datacenter 1")
        self.dc1.save()
        self.dc11 = Datacenter(name="dc1.1", description="Datacenter 1 Row 1")
        self.dc11.save()
        self.dc11.set_parent(self.dc1)
        self.dc12 = Datacenter(name="dc1.2", description="Datacenter 1 Row 2")
        self.dc12.save()
        self.dc12.set_parent(self.dc1)
        self.dc2 = Datacenter(name="dc2", description="Datacenter 2")
        self.dc2.save()

    def setUp(self):
        Datacenter.destroy_all()
        self.create_datacenter_tree()

    def test_list_datacenters(self):
        r = self.get("/api/v1/datacenters/")
        self.assertEqual(r.status_code, 200)
        data = json.loads(r.data)
        self.assertIn("data", data)
        data = data["data"]                     # zombie-zombie-zombie
        self.assertIs(type(data), list)
        self.assertEqual(len(data), 4)

    def test_show_datacenter_by_name(self):
        r = self.get("/api/v1/datacenters/%s" % str(self.dc12.name))
        self.assertEqual(r.status_code, 200)
        data = json.loads(r.data)
        self.assertIn("data", data)
        data = data["data"]
        self.assertIs(type(data), list)
        self.assertEqual(len(data), 1)
        data = data[0]
        self.assertEqual(data["name"], self.dc12.name)
        self.assertEqual(data["description"], self.dc12.description)
        self.assertEqual(data["parent_id"], str(self.dc1._id))

    def test_show_datacenter_by_id(self):
        r = self.get("/api/v1/datacenters/%s" % str(self.dc12._id))
        self.assertEqual(r.status_code, 200)
        data = json.loads(r.data)
        self.assertIn("data", data)
        data = data["data"]
        self.assertIs(type(data), list)
        self.assertEqual(len(data), 1)
        data = data[0]
        self.assertEqual(data["name"], self.dc12.name)
        self.assertEqual(data["description"], self.dc12.description)
        self.assertEqual(data["parent_id"], str(self.dc1._id))

    def test_create_datacenter(self):
        payload = {
            "name": "dc2.1",
            "description": "Datacenter 2 Row 1",
            "parent_id": str(self.dc2._id)
        }
        r = self.post_json("/api/v1/datacenters/", payload)
        self.assertEqual(r.status_code, 200)
        dc21 = Datacenter.find_one({"name": payload["name"]})
        self.assertIsNotNone(dc21)
        self.assertEqual(dc21.description, payload["description"])
        self.assertEqual(dc21.parent_id, self.dc2._id)

    def test_update_datacenter(self):
        payload = {
            "name": "dc3",
            "description": "Datacenter 3",
            "parent_id": None
        }
        r = self.put_json("/api/v1/datacenters/%s" % self.dc12.name, payload)
        self.assertEqual(r.status_code, 200)
        self.dc12.reload()
        self.assertEqual(self.dc12.name, payload["name"])
        self.assertEqual(self.dc12.description, payload["description"])
        self.assertIsNone(self.dc12.parent_id)

    def test_delete_datacenter(self):
        r = self.delete("/api/v1/datacenters/%s" % self.dc12.name)
        self.assertEqual(r.status_code, 200)
        self.assertIsNone(Datacenter.find_one({"_id": self.dc12._id}))

    def test_set_parent(self):
        r = self.put_json("/api/v1/datacenters/%s/set_parent" % self.dc12.name, {"parent_id": str(self.dc2._id)})
        self.assertEqual(r.status_code, 200)
        self.dc12.reload()
        self.assertEqual(self.dc12.parent_id, self.dc2._id)

    def test_unset_parent(self):
        r = self.put_json("/api/v1/datacenters/%s/set_parent" % self.dc12._id, {"parent_id": None})
        self.assertEqual(r.status_code, 200)
        self.dc12.reload()
        self.assertIsNone(self.dc12.parent_id)
