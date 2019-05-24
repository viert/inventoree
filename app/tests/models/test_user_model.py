from unittest import TestCase
from app.models import User, Token
from app.models.storable_model import now
from datetime import datetime, timedelta


class TestUserModel(TestCase):

    @classmethod
    def setUpClass(cls):
        from app import app
        app.auth_token_ttl = timedelta(seconds=100)
        app.auth_token_ttr = timedelta(seconds=10)

    def setUp(self):
        Token.destroy_all()
        User.destroy_all()

    def test_token_expiration(self):
        u = User(username="test_user")
        u.save()

        self.assertEqual(u.tokens.count(), 0)

        _ = u.auth_token
        self.assertEqual(u.tokens.count(), 1)

        t1 = u.tokens[0]
        self.assertFalse(t1.expired())

        t1.created_at = now() - timedelta(seconds=20)  # need renewing
        t1.save()
        self.assertFalse(t1.expired())

        at = u.auth_token
        self.assertNotEqual(at, t1.token, "another token should be issued, time to renew")
        tokens = Token.find({"user_id": u._id})
        self.assertEqual(tokens.count(), 2)

        t1.created_at = now() - timedelta(seconds=120)
        t1.save()
        new_at = u.auth_token
        self.assertEqual(at, new_at, "token should not have changed")
        self.assertEqual(u.tokens.count(), 1, "the first token should be destroyed due to expiration")
