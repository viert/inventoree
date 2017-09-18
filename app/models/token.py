from storable_model import StorableModel, now
from library.engine.utils import uuid4_string


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
        return self.user_class.find_one({ "_id": self.user_id })

    @property
    def user_class(self):
        if self._user_class is None:
            from app.models import User
            self.__class__._user_class = User
        return self._user_class

    @property
    def expired(self):
        # TODO token expiration
        return False