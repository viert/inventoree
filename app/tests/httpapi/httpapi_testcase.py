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
        supervisor = User(username=HttpApiTestCase.SUPERVISOR["username"], supervisor=True, password_raw=HttpApiTestCase.SUPERVISOR["password"])
        supervisor.save()
        token = supervisor.get_auth_token()
        cls.supervisor = supervisor
        cls.token = token.token
        cls.project1 = Project(name="Test Project 1", owner_id=supervisor._id)
        cls.project1.save()
        cls.project2 = Project(name="Test Project 2", owner_id=supervisor._id)
        cls.project2.save()

    @classmethod
    def tearDownClass(cls):
        User.destroy_all()
        Project.destroy_all()
        Group.destroy_all()
        Host.destroy_all()

    @property
    def fake_client(self):
        return app.flask.test_client()

    def get(self, url):
        return self.fake_client.get(url, headers={ "X-Api-Auth-Token": self.token })

    def delete(self, url):
        return self.fake_client.delete(url, headers={ "X-Api-Auth-Token": self.token })

    def post_json(self, url, data):
        data = json.dumps(data, default=app.flask.json_encoder().default)
        return self.fake_client.post(url, data=data, headers={ "Content-Type": "application/json", "X-Api-Auth-Token": self.token })

    def put_json(self, url, data):
        data = json.dumps(data, default=app.flask.json_encoder().default)
        return self.fake_client.put(url, data=data, headers={ "Content-Type": "application/json", "X-Api-Auth-Token": self.token })

