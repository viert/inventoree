from storable_model import StorableModel, now
from library.engine.utils import uuid4_string
from datetime import datetime, timedelta


class Token(StorableModel):

    _user_class = None

    FIELDS = (
        "_id",
        "type",
        "token",
        "user_id",
        "created_at"
    )

    KEY_FIELD = "token"

    REQUIRED_FIELDS = (
        "type",
        "token",
        "user_id",
        "created_at"
    )

    DEFAULTS = {
        "type": "auth",
        "token": uuid4_string,
        "created_at": now
    }

    INDEXES = (
        ["token", {"unique": True}],
        ["user_id", "type"]
    )

    @property
    def user(self):
        return self.user_class.find_one({"_id": self.user_id})

    @property
    def user_class(self):
        if self._user_class is None:
            from app.models import User
            self.__class__._user_class = User
        return self._user_class

    def expired(self):
        from app import app
        if app.auth_token_ttl is None:
            # No token expiration
            return False
        expires_at = self.created_at + app.auth_token_ttl
        return expires_at < now()

    def close_to_expiration(self):
        from app import app
        if app.auth_token_ttr is None:
            # No time to renew
            return False
        renew_at = self.created_at + app.auth_token_ttr
        return renew_at < now()
