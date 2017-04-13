from storable_model import StorableModel, now
from library.engine.pbkdf2 import pbkdf2_hex
from time import mktime

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
        "supervisor": False
    }
    
    REQUIRED_FIELDS = (
        "username",
        "password_hash"
    )

    REJECTED_FIELDS = (
        "password_hash",
        "supervisor",
        "created_at",
        "updated_at",
    )

    __slots__ = list(FIELDS) + ["_salt"]

    @property
    def salt(self):
        if self._salt is None:
            from app import app
            secret_key = app.config.app.get("SECRET_KEY")
            if secret_key is None:
                raise RuntimeError("No SECRET_KEY in app section of config")
            self._salt = "%s.%d" % (secret_key, int(mktime(self.created_at.utctimetuple())))
        return self._salt

    def __init__(self, **kwargs):
        self._salt = None
        ts = now()
        # these should be set before setting salt
        # because salt actually depends on user created_at time
        if not "created_at" in kwargs:
            kwargs["created_at"] = ts
            self.created_at = ts
        if not "updated_at" in kwargs:
            kwargs["updated_at"] = ts
            self.updated_at = ts
        if "password_raw" in kwargs:
            password_raw = kwargs["password_raw"]
            del(kwargs["password_raw"])
            kwargs["password_hash"] = pbkdf2_hex(password_raw, self.salt)
        StorableModel.__init__(self, **kwargs)

    def touch(self):
        self.updated_at = now()

    def _before_save(self):
        self.touch()

    def set_password(self, password_raw):
        self.password_hash = pbkdf2_hex(password_raw, self.salt)

    def check_password(self, password_raw):
        return pbkdf2_hex(password_raw, self.salt) == self.password_hash