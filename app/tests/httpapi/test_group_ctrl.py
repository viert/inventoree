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

    def test_delete_group(self):
        self.test_create_group()
        group = Group.find_one({"name": "group1"})
        with self.authenticated_client() as ac:
            r = ac.delete("/api/v1/groups/%s" % group._id)
            self.assertEqual(r.status_code, 200)
            data = json.loads(r.data)
            self.assertIn("data", data)
            group_data = data["data"]
            self.assertEqual(group_data["_id"], None)
            group = Group.find_one({"_id": group._id})
            self.assertIsNone(group)

    def test_set_children(self):
        g1 = Group(name="g1", project_id=self.project1._id)
        g1.save()
        g2 = Group(name="g2", project_id=self.project1._id)
        g2.save()
        g3 = Group(name="g3", project_id=self.project1._id)
        g3.save()
        g4 = Group(name="g4", project_id=self.project1._id)
        g4.save()

        child_ids = [str(x._id) for x in (g2, g3, g4)]
        payload = {
            "child_ids": child_ids
        }

        with self.authenticated_client() as ac:
            r = self.put_json(ac, "/api/v1/groups/%s/set_children" % g1._id, payload)
            self.assertEqual(r.status_code, 200)
            data = json.loads(r.data)
            self.assertIn("data", data)
            group_data = data["data"]
            self.assertEqual(group_data["_id"], str(g1._id))
            self.assertItemsEqual(group_data["child_ids"], child_ids)
            g1 = Group.find_one({ "_id": g1._id })
            self.assertItemsEqual([str(x) for x in g1.child_ids], child_ids)