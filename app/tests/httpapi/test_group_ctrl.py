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
            "work_group_id": self.work_group1._id,
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
        self.assertEqual(group_attrs["work_group_id"], str(g.work_group_id))

    def test_create_group(self):
        payload = {
            "name": "group1",
            "work_group_id": self.work_group1._id,
            "tags": [ "meaw", "gang", "boo" ]
        }
        r = self.post_json("/api/v1/groups/", payload)
        self.assertEqual(r.status_code, 201)
        data = json.loads(r.data)
        self.assertIn("data", data)
        group = data["data"]
        self.assertEqual(group["name"], payload["name"])
        self.assertEqual(group["work_group_id"], str(payload["work_group_id"]))
        self.assertItemsEqual(group["tags"], payload["tags"])

    def test_create_group_with_work_group_name(self):
        payload = {
            "name": "group1",
            "work_group_name": self.work_group1.name,
            "tags": [ "meaw", "gang", "boo" ]
        }
        r = self.post_json("/api/v1/groups/", payload)
        self.assertEqual(r.status_code, 201)
        data = json.loads(r.data)
        self.assertIn("data", data)
        group = data["data"]
        self.assertEqual(group["name"], payload["name"])
        self.assertEqual(group["work_group_id"], str(self.work_group1._id))
        self.assertItemsEqual(group["tags"], payload["tags"])

    def test_create_group_with_parent(self):
        self.test_create_group()
        parent = Group.find_one({"name": "group1"})

        payload = {
            "name": "group2",
            "work_group_id": self.work_group1._id,
            "parent_group_id": str(parent._id)
        }
        r = self.post_json("/api/v1/groups/", payload)
        self.assertEqual(r.status_code, 201)
        data = json.loads(r.data)
        self.assertIn("data", data)
        group = data["data"]
        self.assertEqual(group["name"], payload["name"])
        self.assertEqual(group["work_group_id"], str(self.work_group1._id))
        self.assertIn(str(parent._id), group["parent_ids"])

    def test_create_group_with_parent_diff_workgroup(self):
        self.test_create_group()
        parent = Group.find_one({"name": "group1"})

        payload = {
            "name": "group2",
            "work_group_id": self.work_group2._id,
            "parent_group_id": str(parent._id)
        }
        r = self.post_json("/api/v1/groups/", payload)
        self.assertEqual(r.status_code, 400)
        data = json.loads(r.data)
        self.assertIn("errors", data)
        errors = data["errors"]
        self.assertEqual(1, len(errors))


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

    def test_group_add_tags(self):
        self.test_create_group()
        group = Group.find_one({"name": "group1"})
        payload = {"tags": ["boo", "sre", "swe"]}
        r = self.post_json("/api/v1/groups/%s/add_tags" % group._id, payload)
        self.assertEqual(r.status_code, 200)
        group.reload()
        self.assertItemsEqual(["boo", "sre", "swe", "meaw", "gang"], group.tags)

    def test_group_remove_tags(self):
        self.test_create_group()
        group = Group.find_one({"name": "group1"})
        payload = {"tags": ["boo", "sre", "swe"]}
        r = self.post_json("/api/v1/groups/%s/remove_tags" % group._id, payload)
        self.assertEqual(r.status_code, 200)
        group.reload()
        self.assertItemsEqual(["meaw", "gang"], group.tags)

    def test_group_set_custom_fields(self):
        attrs = {"name": "group1", "work_group_id": self.work_group1._id, "custom_fields": [{"key": "key1", "value": "value1"}]}
        group = Group(**attrs)
        group.save()

        payload = {"custom_fields": [{"key": "key2", "value": "value2"}]}
        r = self.post_json("/api/v1/groups/%s/set_custom_fields" % group._id, payload)
        self.assertEqual(r.status_code, 200)
        group.reload()
        self.assertItemsEqual([{"key": "key1", "value": "value1"}, {"key": "key2", "value": "value2"}], group.custom_fields)

        payload = {"custom_fields": {"key3": "value3", "key1": "newvalue1"}}
        r = self.post_json("/api/v1/groups/%s/set_custom_fields" % group._id, payload)
        self.assertEqual(r.status_code, 200)
        group.reload()
        self.assertItemsEqual([{"key": "key1", "value": "newvalue1"},
                               {"key": "key2", "value": "value2"},
                               {"key": "key3", "value": "value3"}], group.custom_fields)

    def test_group_remove_custom_fields(self):
        attrs = {"name": "group1", "work_group_id": self.work_group1._id, "custom_fields": [
            {"key": "key1", "value": "value1"},
            {"key": "key2", "value": "value2"},
        ]}
        group = Group(**attrs)
        group.save()

        payload = {"custom_fields": [{"key": "key2"}, {"key": "key4"}]}
        r = self.post_json("/api/v1/groups/%s/remove_custom_fields" % group._id, payload)
        self.assertEqual(r.status_code, 200)
        group.reload()
        self.assertItemsEqual([{"key": "key1", "value": "value1"}], group.custom_fields)

        payload = {"custom_fields": {"key3": None, "key1": None}}
        r = self.post_json("/api/v1/groups/%s/remove_custom_fields" % group._id, payload)
        self.assertEqual(r.status_code, 200)
        group.reload()
        self.assertItemsEqual([], group.custom_fields)

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
        g1 = Group(name="g1", work_group_id=self.work_group1._id)
        g1.save()
        g2 = Group(name="g2", work_group_id=self.work_group1._id)
        g2.save()
        g3 = Group(name="g3", work_group_id=self.work_group1._id)
        g3.save()
        g4 = Group(name="g4", work_group_id=self.work_group1._id)
        g4.save()
        g1.add_child(g2)
        g2.add_child(g3)
        g3.add_child(g4)
        group_ids = [str(g2._id), str(g3._id)]

        # insufficient permissions
        r = self.post_json("/api/v1/groups/mass_delete", {"group_ids": group_ids}, supervisor=False)
        self.assertEqual(403, r.status_code)

        # supervisor permissions
        r = self.post_json("/api/v1/groups/mass_delete", { "group_ids": group_ids })
        self.assertEqual(200, r.status_code)
        deleted_groups = Group.find({"_id": {"$in":[g2._id, g3._id]}})
        self.assertEqual(0, deleted_groups.count())
        g1 = Group.find_one({"_id":g1._id})
        self.assertEqual(0, len(g1.child_ids))
        g4 = Group.find_one({"_id":g4._id})
        self.assertEqual(0, len(g4.parent_ids))

    def test_set_children(self):
        g1 = Group(name="g1", work_group_id=self.work_group1._id)
        g1.save()
        g2 = Group(name="g2", work_group_id=self.work_group1._id)
        g2.save()
        g3 = Group(name="g3", work_group_id=self.work_group1._id)
        g3.save()
        g4 = Group(name="g4", work_group_id=self.work_group1._id)
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
        g1 = Group(name="g1", work_group_id=self.work_group1._id)
        g1.save()
        g2 = Group(name="g2", work_group_id=self.work_group1._id)
        g2.save()
        g3 = Group(name="g3", work_group_id=self.work_group1._id)
        g3.save()
        g4 = Group(name="g4", work_group_id=self.work_group1._id)
        g4.save()

        g1.add_child(g2)
        g2.add_child(g3)
        g3.add_child(g4)

        # 400, no group_ids given
        r = self.post_json("/api/v1/groups/mass_move", { "work_group_id": str(self.work_group2._id) })
        self.assertEqual(r.status_code, 400)

        # 400, no work_group_id given
        r = self.post_json("/api/v1/groups/mass_move", { "group_ids": [str(g2._id)] })
        self.assertEqual(r.status_code, 400)

        # 400, invalid group_ids type
        r = self.post_json("/api/v1/groups/mass_move", { "work_group_id": str(self.work_group2._id), "group_ids": str(g2._id) })
        self.assertEqual(r.status_code, 400)

        # group is already in the work_group - 404, no group suitable for moving found
        r = self.post_json("/api/v1/groups/mass_move", { "work_group_id": str(self.work_group1._id), "group_ids": [str(g2._id)] })
        self.assertEqual(r.status_code, 404)

        # no work_group found
        r = self.post_json("/api/v1/groups/mass_move", { "work_group_id": str(ObjectId()), "group_ids": [str(g2._id)] })
        self.assertEqual(r.status_code, 404)

        # insufficient permissions
        payload = {
            "group_ids": [str(g2._id)],
            "work_group_id": str(self.work_group2._id)
        }
        r = self.post_json("/api/v1/groups/mass_move", payload, supervisor=False)
        self.assertEqual(r.status_code, 403)

        # real case
        r = self.post_json("/api/v1/groups/mass_move", payload)
        self.assertEqual(r.status_code, 200)

        # reload groups
        g1 = Group.find_one({ "_id": g1._id })
        g2 = Group.find_one({ "_id": g2._id })
        g3 = Group.find_one({ "_id": g3._id })
        g4 = Group.find_one({ "_id": g4._id })

        # group 1 should have remained in work_group1
        self.assertEqual(g1.work_group_id, self.work_group1._id)

        # groups 2, 3, 4 should have been moved to work_group2
        self.assertEqual(g2.work_group_id, self.work_group2._id)
        self.assertEqual(g3.work_group_id, self.work_group2._id)
        self.assertEqual(g4.work_group_id, self.work_group2._id)

        # group 2 should have been detached from g1
        self.assertItemsEqual([], g2.parent_ids)
        self.assertItemsEqual([], g1.child_ids)

        # groups 3, 4 should have kept its' parents
        self.assertItemsEqual([g2._id], g3.parent_ids)
        self.assertItemsEqual([g3._id], g4.parent_ids)

    def test_custom_data_change_parent(self):
        g1 = Group(name="g1", work_group_id=self.work_group1._id,
                   local_custom_data={
                       "group1data": "group1",
                       "common": {
                           "group1": 1,
                           "all": 2,
                       }
                   })
        g1.save()
        g2 = Group(name="g2", work_group_id=self.work_group1._id,
                   local_custom_data={
                       "group2data": "group2",
                       "common": {
                           "group2": 2,
                           "all": 3
                       }
                   })
        g2.save()

        r = self.put_json("/api/v1/groups/%s/set_children" % g1.name, {"child_ids": [str(g2._id)]})
        self.assertEqual(200, r.status_code)

        g2.reload()
        self.assertDictEqual(
            g2.custom_data,
            {
                "group1data": "group1",
                "group2data": "group2",
                "common": {
                    "group1": 1,
                    "group2": 2,
                    "all": 3,
                }
            }
        )

        r = self.put_json("/api/v1/groups/%s/set_children" % g1.name, {"child_ids": []})
        self.assertEqual(200, r.status_code)
        g2.reload()
        self.assertDictEqual(
            g2.custom_data,
            {
                "group2data": "group2",
                "common": {
                    "group2": 2,
                    "all": 3
                }
            }
        )

    def test_mine_list(self):
        g1 = Group(name="mine", work_group_id=self.work_group1._id)
        g1.save()
        g2 = Group(name="notmine", work_group_id=self.work_group2._id)
        g2.save()

        r = self.get("/api/v1/groups/", supervisor=True)
        self.assertEqual(200, r.status_code)
        data = json.loads(r.data)
        self.assertIn("data", data)
        data = data["data"]
        self.assertIs(type(data), list)
        names = [x["name"] for x in data]
        self.assertIn("mine", names)
        self.assertIn("notmine", names)

        r = self.get("/api/v1/groups/?_mine=true", supervisor=True)
        data = json.loads(r.data)
        self.assertIn("data", data)
        data = data["data"]
        self.assertIs(type(data), list)
        names = [x["name"] for x in data]
        self.assertIn("mine", names)
        self.assertNotIn("notmine", names)
