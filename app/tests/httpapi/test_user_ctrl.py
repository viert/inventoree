from httpapi_testcase import HttpApiTestCase
from flask import json
from app.models import User
from copy import copy

class TestUserCtrl(HttpApiTestCase):

    NEW_USER = {
        "username": "new_user_for_testing",
        "first_name": "Test",
        "last_name": "Case"
    }

    def tearDown(self):
        nu = User.find_one({"username": self.NEW_USER["username"]})
        if nu is not None:
            nu.destroy()

        nu = User.find_one({"username": "changed_username"})
        if nu is not None:
            nu.destroy()

    def test_list_users(self):
        r = self.get("/api/v1/users/")
        self.assertEqual(r.status_code, 200)
        body = json.loads(r.data)
        self.assertIn("data", body)
        self.assertIsInstance(body["data"], list)
        self.assertIs(3, len(body["data"]))

    def test_get_user(self):
        r = self.get("/api/v1/users/%s?_fields=username,auth_token" % self.supervisor._id, supervisor=False)
        self.assertEqual(r.status_code, 200)
        body = json.loads(r.data)
        self.assertIn("data", body)
        self.assertIsInstance(body["data"], list)
        self.assertIs(1, len(body["data"]))
        user_data = body["data"][0]
        self.assertEqual(user_data["username"], self.supervisor.username)
        self.assertIn("auth_token", user_data)
        self.assertIsNone(user_data["auth_token"])

    def test_get_user_supervisor(self):
        r = self.get("/api/v1/users/%s?_fields=username,auth_token" % self.supervisor._id, supervisor=True)
        self.assertEqual(r.status_code, 200)
        body = json.loads(r.data)
        self.assertIn("data", body)
        self.assertIsInstance(body["data"], list)
        self.assertIs(1, len(body["data"]))
        user_data = body["data"][0]
        self.assertEqual(user_data["username"], self.supervisor.username)
        self.assertIn("auth_token", user_data)

    def test_user_create(self):
        r = self.post_json("/api/v1/users/", self.NEW_USER)
        self.assertEqual(r.status_code, 200)
        body = json.loads(r.data)
        self.assertIn("data", body)
        self.assertIsInstance(body["data"], dict)
        user_data = body["data"]
        self.assertEqual(user_data["username"], self.NEW_USER["username"])
        user_id = user_data["_id"]
        user = User.get(user_id)
        self.assertEqual(user.username, self.NEW_USER["username"])

    def test_user_create_insufficient(self):
        r = self.post_json("/api/v1/users/", self.NEW_USER, supervisor=False)
        self.assertEqual(r.status_code, 403)

    def test_user_create_existing(self):
        r = self.post_json("/api/v1/users/", {"username": self.supervisor.username})
        self.assertEqual(r.status_code, 409)

    def test_user_create_passwords_mismatch(self):
        new_user = copy(self.NEW_USER)
        new_user["password_raw"] = "123"
        new_user["password_raw_confirm"] = "456"
        r = self.post_json("/api/v1/users/", new_user)
        self.assertEqual(r.status_code, 400)

    def test_passwd(self):
        new_user = copy(self.NEW_USER)
        password = "super$ecr3t"
        new_user["password_raw"] = password
        new_user["password_raw_confirm"] = password
        r = self.post_json("/api/v1/users/", new_user)
        self.assertEqual(r.status_code, 200)

        # trying to log in with the new credentials
        r = self.fake_client.post("/api/v1/account/authenticate", data=json.dumps({"username":new_user["username"], "password": password}), headers={ "Content-Type": "application/json" })
        self.assertEqual(r.status_code, 200)

    def test_update(self):
        new_user = copy(self.NEW_USER)
        password = "super$ecr3t"
        new_user["password_raw"] = password
        new_user["password_raw_confirm"] = password
        r = self.post_json("/api/v1/users/", new_user)
        self.assertEqual(r.status_code, 200)
        user_id = json.loads(r.data)["data"]["_id"]
        user = User.get(user_id)

        r = self.put_json("/api/v1/users/%s" % user_id, {"username": "changed_username"})
        self.assertEqual(r.status_code, 200)
        user = User.get(user_id)
        self.assertEqual(user.username, "changed_username")

    def test_set_password(self):
        r = self.put_json(
            "/api/v1/users/%s/set_password" % self.user.username,
           {
               "password_raw": "123",
               "password_raw_confirm": "456"
           }
        )
        self.assertEqual(r.status_code, 400)
        r = self.put_json(
            "/api/v1/users/%s/set_password" % self.user.username,
            {
                "password_raw": "newpwd",
                "password_raw_confirm": "newpwd"
            }
        )
        self.assertEqual(r.status_code, 200)
        # trying to log in with the new credentials
        r = self.fake_client.post(
            "/api/v1/account/authenticate",
            data=json.dumps(
                {
                    "username": self.user.username,
                    "password": "newpwd"
                }
            ),
            headers={
                "Content-Type": "application/json"
            }
        )
        self.assertEqual(r.status_code, 200)

    def test_set_supervisor(self):
        r = self.put_json(
            "/api/v1/users/%s/set_supervisor" % self.user.username,
            {"supervisor": True}
        )
        self.assertEqual(r.status_code, 200)
        user = User.get(self.user.username)
        self.assertTrue(user.supervisor)

        r = self.put_json(
            "/api/v1/users/%s/set_supervisor" % self.user.username,
            {"supervisor": False}
        )
        self.assertEqual(r.status_code, 200)
        user = User.get(self.user.username)
        self.assertFalse(user.supervisor)

    def test_cant_unset_supervisor_on_self(self):
        r = self.put_json(
            "/api/v1/users/%s/set_supervisor" % self.supervisor.username,
            {"supervisor": False}, supervisor=True
        )
        self.assertEqual(r.status_code, 403)

    def test_delete_user(self):
        u = User(**self.NEW_USER)
        u.save()
        r = self.delete("/api/v1/users/%s" % u.username)
        self.assertEqual(r.status_code, 200)
        