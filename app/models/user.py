from storable_model import StorableModel, now
from library.engine.pbkdf2 import pbkdf2_hex

class User(StorableModel):

    FIELDS = (
        "_id",
        "username",
        "first_name",
        "last_name",
        "avatar_url",
        "password_hash",
        "created_at",
        "updated_at",
        "supervisor",
    )

    DEFAULTS = {
        "first_name": "",
        "last_name": "",
        "avatar_url": "",
        "created_at": now,
        "updated_at": now,
        "supervisor": False
    }
    
    REQUIRED_FIELDS = (
        "username",
        "password_hash"
    )

    REJECTED_FIELDS = (
        "password_hash",
        "supervisor",
    )

    __slots__ = list(FIELDS) + ["_salt"]

    @property
    def salt(self):
        if self._salt is None:
            from app import app
            self._salt = app.config.app.get("SECRET_KEY")
            if self._salt is None:
                raise RuntimeError("No SECRET_KEY in app section of config")
        return self._salt

    def __init__(self, **kwargs):
        self._salt = None
        if "password_raw" in kwargs:
            password_raw = kwargs["password_raw"]
            del(kwargs["password_raw"])
            kwargs["password_hash"] = pbkdf2_hex(password_raw, self.salt)
        StorableModel.__init__(self, **kwargs)

    def setPassword(self, password_raw):
        self.password_hash = pbkdf2_hex(password_raw, self.salt)