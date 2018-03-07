import flask.json as json
from httpapi_testcase import HttpApiTestCase


class TestAccountCtrl(HttpApiTestCase):
    def test_not_authenticated(self):
        r = self.fake_client.get("/api/v1/account/me")
        self.assertEqual(r.status_code, 403)
        body = json.loads(r.data)
        self.assertIn("state", body)
        self.assertEqual("logged out", body["state"])

    def test_authenticate(self):
        r = self.fake_client.post("/api/v1/account/authenticate", data=json.dumps(self.SUPERVISOR), headers={ "Content-Type": "application/json" })
        self.assertEqual(r.status_code, 200)
        self.assertIn("Set-Cookie", r.headers)

    def test_me(self):
        r = self.get("/api/v1/account/me")
        self.assertEqual(r.status_code, 200)
        body = json.loads(r.data)
        self.assertIn("data", body)
        body = body["data"]
        self.assertIn("_id", body)
        self.assertIn("username", body)
        self.assertEqual(body["username"], TestAccountCtrl.SUPERVISOR["username"])