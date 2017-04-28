import flask.json as json
from httpapi_testcase import HttpApiTestCase
from app import app


class TestAccountCtrl(HttpApiTestCase):
    def test_not_authenticated(self):
        with self.fake_client() as c:
            r = c.get("/api/v1/account/me")
            self.assertEqual(r.status_code, 403)
            body = json.loads(r.data)
            self.assertIn("state", body)
            self.assertEqual("logged out", body["state"])

    def test_authenticate(self):
        with self.fake_client() as c:
            r = c.post("/api/v1/account/authenticate", data=json.dumps(self.SUPERVISOR), headers={ "Content-Type": "application/json" })
            self.assertEqual(r.status_code, 200)
            self.assertIn("Set-Cookie", r.headers)

    def test_me(self):
        with self.authenticated_client() as ac:
            r = ac.get("/api/v1/account/me")
            self.assertEqual(r.status_code, 200)
            body = json.loads(r.data)
            self.assertIn("data", body)
            body = body["data"]
            self.assertIn("_id", body)
            self.assertIn("username", body)
            self.assertEqual(body["username"], TestAccountCtrl.SUPERVISOR["username"])