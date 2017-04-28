from unittest import TestCase
from app.models import User, Project, Group, Host
from app import app
from flask import json


class HttpApiTestCase(TestCase):
    SUPERVISOR = {
        "username": "super",
        "password": "superpasswd"
    }

    @classmethod
    def setUpClass(cls):
        cls.session = None
        User.destroy_all()
        supervisor = User(username=HttpApiTestCase.SUPERVISOR["username"], password_raw=HttpApiTestCase.SUPERVISOR["password"])
        supervisor.save()
        cls.supervisor = supervisor
        cls.project1 = Project(name="Test Project 1", owner_id=supervisor._id)
        cls.project1.save()

    @classmethod
    def tearDownClass(cls):
        User.destroy_all()
        Project.destroy_all()
        Group.destroy_all()
        Host.destroy_all()

    @staticmethod
    def fake_client():
        return app.flask.test_client()

    def extract_session(self, response):
        if "Set-Cookie" in response.headers:
            from Cookie import BaseCookie
            cookie = BaseCookie()
            cookie.load(response.headers["Set-Cookie"])
            self.session = cookie["session"]

    def authenticate(self):
        with self.fake_client() as c:
            r = c.post("/api/v1/account/authenticate", data=json.dumps(self.SUPERVISOR), headers={ "Content-Type": "application/json" })
            self.extract_session(r)

    def post_json(self, client, url, data):
        data = json.dumps(data, default=app.flask.json_encoder().default)
        return client.post(url, data=data, headers={ "Content-Type": "application/json" })

    def put_json(self, client, url, data):
        data = json.dumps(data, default=app.flask.json_encoder().default)
        return client.put(url, data=data, headers={ "Content-Type": "application/json" })

    def authenticated_client(self):
        c = app.flask.test_client()
        if self.session is None:
            self.authenticate()
        c.set_cookie("localhost", "session", self.session.value, httponly=self.session["httponly"], path=self.session["path"], expires=self.session["expires"])
        return c
