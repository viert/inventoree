from unittest import TestCase
from app.models import User, WorkGroup, Group, Host
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

    SYSTEM_USER = {
        "username": "sys",
        "password": "syspassword"
    }

    SYSTEM_SUPERVISOR = {
        "username": "supersys",
        "password": "supersyspassword"
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

        system = User(username=HttpApiTestCase.SYSTEM_USER["username"],
                      supervisor=False,
                      system=True,
                      password_raw=HttpApiTestCase.SYSTEM_USER["password"])
        system.save()

        supersystem = User(username=HttpApiTestCase.SYSTEM_SUPERVISOR["username"],
                           supervisor=True,
                           system=True,
                           password_raw=HttpApiTestCase.SYSTEM_SUPERVISOR["password"])
        supersystem.save()

        supertoken = supervisor.get_auth_token()
        usertoken = user.get_auth_token()
        systemtoken = system.get_auth_token()
        systemsupertoken = supersystem.get_auth_token()

        cls.supervisor = supervisor
        cls.supertoken = supertoken.token

        cls.user = user
        cls.usertoken = usertoken.token

        cls.systemuser = system
        cls.systemtoken = systemtoken.token

        cls.systemsuperuser = supersystem
        cls.systemsupertoken = systemsupertoken.token

        cls.work_group1 = WorkGroup(name="Test WorkGroup 1", owner_id=supervisor._id)
        cls.work_group1.save()
        cls.work_group2 = WorkGroup(name="Test WorkGroup 2", owner_id=user._id)
        cls.work_group2.save()
        cls.work_group2.add_member(system)

    @classmethod
    def tearDownClass(cls):
        User.destroy_all()
        WorkGroup.destroy_all()
        Group.destroy_all()
        Host.destroy_all()

    @property
    def fake_client(self):
        return app.flask.test_client()

    def get_proper_token(self, supervisor, system):
        if supervisor:
            if system:
                return self.systemsupertoken
            else:
                return self.supertoken
        elif system:
            return self.systemtoken
        return self.usertoken

    def get(self, url, supervisor=True, system=False):
        token = self.get_proper_token(supervisor, system)
        return self.fake_client.get(url, headers={ "X-Api-Auth-Token": token })

    def delete(self, url, supervisor=True, system=False):
        token = self.get_proper_token(supervisor, system)
        return self.fake_client.delete(url, headers={ "X-Api-Auth-Token": token })

    def post_json(self, url, data, supervisor=True, system=False):
        token = self.get_proper_token(supervisor, system)
        data = json.dumps(data, default=app.flask.json_encoder().default)
        return self.fake_client.post(url, data=data, headers={ "Content-Type": "application/json", "X-Api-Auth-Token": token })

    def put_json(self, url, data, supervisor=True, system=False):
        token = self.get_proper_token(supervisor, system)
        data = json.dumps(data, default=app.flask.json_encoder().default)
        return self.fake_client.put(url, data=data, headers={ "Content-Type": "application/json", "X-Api-Auth-Token": token })

    def get_json_data_should_be_successful(self, url, **kwargs):
        r = self.get(url, **kwargs)
        self.assertEqual(200, r.status_code)
        return json.loads(r.data)