from httpapi_testcase import HttpApiTestCase
from flask import json
from app.models import Group

class TestGroupCtrl(HttpApiTestCase):

    def setUp(self):
        Group.destroy_all()

    def test_create_group(self):
        payload = {
            "name": "group1",
            "project_id": self.project1._id,
            "tags": [ "meaw", "gang", "boo" ]
        }
        with self.authenticated_client() as ac:
            r = self.post_json(ac, "/api/v1/groups/", payload)
            self.assertEqual(r.status_code, 201)
            data = json.loads(r.data)
            self.assertIn("data", data)
            group = data["data"]
            self.assertEqual(group["name"], payload["name"])
            self.assertEqual(group["project_id"], str(payload["project_id"]))
            self.assertItemsEqual(group["tags"], payload["tags"])

    def test_update_group(self):
        self.test_create_group()
        group = Group.find_one({"name": "group1"})
        payload = {
            "tags": ["support", "sre", "swe"],
            "name": "group2",
            "description": "my mega description"
        }
        with self.authenticated_client() as ac:
            r = self.put_json(ac, "/api/v1/groups/%s" % group._id, payload)
            self.assertEqual(r.status_code, 200)
            data = json.loads(r.data)
            self.assertIn("data", data)
            group = data["data"]
            self.assertEqual(group["name"], payload["name"])
            self.assertEqual(group["description"], payload["description"])
            self.assertItemsEqual(group["tags"], payload["tags"])
