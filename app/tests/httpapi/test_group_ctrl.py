from httpapi_testcase import HttpApiTestCase
from flask import json
from app.models import Group
from bson.objectid import ObjectId


class TestGroupCtrl(HttpApiTestCase):

    def setUp(self):
        Group.destroy_all()

    def test_show_group(self):
        payload = {
            "name": "group1",
            "project_id": self.project1._id,
            "tags": [ "meaw", "gang", "boo" ]
        }
        g = Group(**payload)
        g.save()
        r = self.get("/api/v1/groups/%s" % g._id)
        self.assertEqual(200, r.status_code)
        data = json.loads(r.data)
        self.assertIn("data", data)
        data = data["data"]
        self.assertIs(list, type(data))
        self.assertEqual(1, len(data))
        group_attrs = data[0]
        self.assertEqual(group_attrs["name"], g.name)
        self.assertItemsEqual(group_attrs["tags"], g.tags)
        self.assertEqual(group_attrs["project_id"], str(g.project_id))

    def test_create_group(self):
        payload = {
            "name": "group1",
            "project_id": self.project1._id,
            "tags": [ "meaw", "gang", "boo" ]
        }
        r = self.post_json("/api/v1/groups/", payload)
        self.assertEqual(r.status_code, 201)
        data = json.loads(r.data)
        self.assertIn("data", data)
        group = data["data"]
        self.assertEqual(group["name"], payload["name"])
        self.assertEqual(group["project_id"], str(payload["project_id"]))
        self.assertItemsEqual(group["tags"], payload["tags"])

    def test_create_group_with_project_name(self):
        payload = {
            "name": "group1",
            "project_name": self.project1.name,
            "tags": [ "meaw", "gang", "boo" ]
        }
        r = self.post_json("/api/v1/groups/", payload)
        self.assertEqual(r.status_code, 201)
        data = json.loads(r.data)
        self.assertIn("data", data)
        group = data["data"]
        self.assertEqual(group["name"], payload["name"])
        self.assertEqual(group["project_id"], str(self.project1._id))
        self.assertItemsEqual(group["tags"], payload["tags"])

    def test_update_group(self):
        self.test_create_group()
        group = Group.find_one({"name": "group1"})
        payload = {
            "tags": ["support", "sre", "swe"],
            "name": "group2",
            "description": "my mega description"
        }
        r = self.put_json("/api/v1/groups/%s" % group._id, payload)
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
        r = self.delete("/api/v1/groups/%s" % group._id)
        self.assertEqual(r.status_code, 200)
        data = json.loads(r.data)
        self.assertIn("data", data)
        group_data = data["data"]
        self.assertEqual(group_data["_id"], None)
        group = Group.find_one({"_id": group._id})
        self.assertIsNone(group)

    def test_mass_delete(self):
        g1 = Group(name="g1", project_id=self.project1._id)
        g1.save()
        g2 = Group(name="g2", project_id=self.project1._id)
        g2.save()
        g3 = Group(name="g3", project_id=self.project1._id)
        g3.save()
        g4 = Group(name="g4", project_id=self.project1._id)
        g4.save()
        g1.add_child(g2)
        g2.add_child(g3)
        g3.add_child(g4)
        group_ids = [str(g2._id), str(g3._id)]
        r = self.post_json("/api/v1/groups/mass_delete", { "group_ids": group_ids })
        self.assertEqual(200, r.status_code)
        deleted_groups = Group.find({"_id": {"$in":[g2._id, g3._id]}})
        self.assertEqual(0, deleted_groups.count())
        g1 = Group.find_one({"_id":g1._id})
        self.assertEqual(0, len(g1.child_ids))
        g4 = Group.find_one({"_id":g4._id})
        self.assertEqual(0, len(g4.parent_ids))


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

        r = self.put_json("/api/v1/groups/%s/set_children" % g1._id, payload)
        self.assertEqual(r.status_code, 200)
        data = json.loads(r.data)
        self.assertIn("data", data)
        group_data = data["data"]
        self.assertEqual(group_data["_id"], str(g1._id))
        self.assertItemsEqual(group_data["child_ids"], child_ids)
        g1 = Group.find_one({ "_id": g1._id })
        self.assertItemsEqual([str(x) for x in g1.child_ids], child_ids)


    def test_mass_move(self):
        g1 = Group(name="g1", project_id=self.project1._id)
        g1.save()
        g2 = Group(name="g2", project_id=self.project1._id)
        g2.save()
        g3 = Group(name="g3", project_id=self.project1._id)
        g3.save()
        g4 = Group(name="g4", project_id=self.project1._id)
        g4.save()

        g1.add_child(g2)
        g2.add_child(g3)
        g3.add_child(g4)

        # 400, no group_ids given
        r = self.post_json("/api/v1/groups/mass_move", { "project_id": str(self.project2._id) })
        self.assertEqual(r.status_code, 400)

        # 400, no project_id given
        r = self.post_json("/api/v1/groups/mass_move", { "group_ids": [str(g2._id)] })
        self.assertEqual(r.status_code, 400)

        # 400, invalid group_ids type
        r = self.post_json("/api/v1/groups/mass_move", { "project_id": str(self.project2._id), "group_ids": str(g2._id) })
        self.assertEqual(r.status_code, 400)

        # group is already in the project - 404, no group suitable for moving found
        r = self.post_json("/api/v1/groups/mass_move", { "project_id": str(self.project1._id), "group_ids": [str(g2._id)] })
        self.assertEqual(r.status_code, 404)

        # no project found
        r = self.post_json("/api/v1/groups/mass_move", { "project_id": str(ObjectId()), "group_ids": [str(g2._id)] })
        self.assertEqual(r.status_code, 404)

        # real case
        payload = {
            "group_ids": [str(g2._id)],
            "project_id": str(self.project2._id)
        }

        r = self.post_json("/api/v1/groups/mass_move", payload)
        self.assertEqual(r.status_code, 200)

        # reload groups
        g1 = Group.find_one({ "_id": g1._id })
        g2 = Group.find_one({ "_id": g2._id })
        g3 = Group.find_one({ "_id": g3._id })
        g4 = Group.find_one({ "_id": g4._id })

        # group 1 should have remained in project1
        self.assertEqual(g1.project_id, self.project1._id)

        # groups 2, 3, 4 should have been moved to project2
        self.assertEqual(g2.project_id, self.project2._id)
        self.assertEqual(g3.project_id, self.project2._id)
        self.assertEqual(g4.project_id, self.project2._id)

        # group 2 should have been detached from g1
        self.assertItemsEqual([], g2.parent_ids)
        self.assertItemsEqual([], g1.child_ids)

        # groups 3, 4 should have kept its' parents
        self.assertItemsEqual([g2._id], g3.parent_ids)
        self.assertItemsEqual([g3._id], g4.parent_ids)