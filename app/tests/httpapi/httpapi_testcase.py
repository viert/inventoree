from unittest import TestCase
from app.models import User, Project, Group, Host
from app import app
from flask import json


class HttpApiTestCase(TestCase):
    SUPERVISOR = {
        "username": "super",
        "password": "superpasswd"
    }

    GENERAL_USER = {
        "username": "user",
        "password": "userpassword"
    }

    @classmethod
    def setUpClass(cls):
        cls.session = None
        User.destroy_all()
        supervisor = User(username=HttpApiTestCase.SUPERVISOR["username"],
                          supervisor=True,
                          password_raw=HttpApiTestCase.SUPERVISOR["password"])
        supervisor.save()

        user = User(username=HttpApiTestCase.GENERAL_USER["username"],
                    supervisor=False,
                    password_raw=HttpApiTestCase.GENERAL_USER["password"])
        user.save()

        supertoken = supervisor.get_auth_token()
        usertoken = user.get_auth_token()

        cls.supervisor = supervisor
        cls.supertoken = supertoken.token

        cls.user = user
        cls.usertoken = usertoken.token

        cls.project1 = Project(name="Test Project 1", owner_id=supervisor._id)
        cls.project1.save()
        cls.project2 = Project(name="Test Project 2", owner_id=user._id)
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

    def get(self, url, supervisor=True):
        token = self.supertoken if supervisor else self.usertoken
        return self.fake_client.get(url, headers={ "X-Api-Auth-Token": token })

    def delete(self, url, supervisor=True):
        token = self.supertoken if supervisor else self.usertoken
        return self.fake_client.delete(url, headers={ "X-Api-Auth-Token": token })

    def post_json(self, url, data, supervisor=True):
        token = self.supertoken if supervisor else self.usertoken
        data = json.dumps(data, default=app.flask.json_encoder().default)
        return self.fake_client.post(url, data=data, headers={ "Content-Type": "application/json", "X-Api-Auth-Token": token })

    def put_json(self, url, data, supervisor=True):
        token = self.supertoken if supervisor else self.usertoken
        data = json.dumps(data, default=app.flask.json_encoder().default)
        return self.fake_client.put(url, data=data, headers={ "Content-Type": "application/json", "X-Api-Auth-Token": token })
