from storable_model import StorableModel, now
from library.engine.pbkdf2 import pbkdf2_hex
from library.engine.utils import get_user_from_app_context
from library.engine.cache import request_time_cache
from time import mktime
import bcrypt


class UserHasProjects(Exception):
    pass


class User(StorableModel):

    _token_class = None

    FIELDS = (
        "_id",
        "ext_id",
        "username",
        "first_name",
        "last_name",
        "email",
        "avatar_url",
        "password_hash",
        "created_at",
        "updated_at",
        "supervisor",
        "custom_data"
    )

    KEY_FIELD = "username"

    DEFAULTS = {
        "first_name": "",
        "last_name": "",
        "avatar_url": "",
        "supervisor": False,
        "password_hash": "-",
        "email": "",
        "custom_data": {},
        "ext_id": None
    }

    RESTRICTED_FIELDS = [
        "password_hash",
        "tokens"
    ]

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

    INDEXES = (
        ["username",{"unique":True}],
        "ext_id",
        "custom_data",
        "supervisor",
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

    def __set_legacy_password_hash(self, password_raw):
        if not self.created_at:
            ts = now()
            self.created_at = ts
        self.password_hash = pbkdf2_hex(str(password_raw), self.salt)

    def __check_legacy_password_hash(self, password_raw):
        return pbkdf2_hex(str(password_raw), self.salt) == self.password_hash

    def __set_password_hash(self, password_raw):
        if type(password_raw) != unicode:
            password_raw = unicode(password_raw)
        self.password_hash = bcrypt.hashpw(password_raw.encode('utf-8'), bcrypt.gensalt())

    def __check_password_hash(self, password_raw):
        if type(password_raw) != unicode:
            password_raw = unicode(password_raw)
        if type(self.password_hash) != unicode:
            self.password_hash = unicode(self.password_hash)
        return bcrypt.checkpw(password_raw.encode('utf-8'), self.password_hash.encode('utf-8'))

    def __init__(self, **kwargs):
        if "password_raw" in kwargs:
            password_raw = kwargs["password_raw"]
            del(kwargs["password_raw"])
        else:
            password_raw = None
        StorableModel.__init__(self, **kwargs)

        self._salt = None
        if password_raw is not None:
            from app import app
            if app.config.app.get("LEGACY_PASSWORDS", False):
                self.__set_legacy_password_hash(password_raw)
            else:
                self.__set_password_hash(password_raw)

    def touch(self):
        self.updated_at = now()

    def _before_save(self):
        self.touch()

    def _before_delete(self):
        if self.projects_owned.count() > 0:
            raise UserHasProjects("Can't remove user with projects owned by")
        for project in self.projects_included_into:
            project.remove_member(self)

    def set_password(self, password_raw):
        from app import app
        if app.config.app.get("LEGACY_PASSWORDS", False):
            self.__set_legacy_password_hash(password_raw)
        else:
            self.__set_password_hash(password_raw)

    def check_password(self, password_raw):
        from app import app
        if app.config.app.get("LEGACY_PASSWORDS", False):
            return self.__check_legacy_password_hash(password_raw)
        else:
            return self.__check_password_hash(password_raw)

    @property
    def token_class(self):
        if self._token_class is None:
            from app.models import Token
            self.__class__._token_class = Token
        return self._token_class

    @property
    def tokens(self):
        return self.token_class.find({ "user_id": self._id })

    def get_auth_token(self):
        tokens = self.token_class.find({ "type": "auth", "user_id": self._id })
        for token in tokens:
            if not token.expired:
                return token
        token = self.token_class(type="auth", user_id=self._id)
        token.save()
        return token

    @property
    @request_time_cache()
    def projects_owned(self):
        from app.models import Project
        return Project.find({"owner_id": self._id})

    @property
    @request_time_cache()
    def projects_included_into(self):
        from app.models import Project
        return Project.find({"member_ids": self._id})

    @property
    def modification_allowed(self):
        user = get_user_from_app_context()
        if user is None: return False
        if user.supervisor or self._id == user._id: return True
        return False

    @property
    def supervisor_set_allowed(self):
        user = get_user_from_app_context()
        return user.supervisor and user._id != self._id
        # user can't revoke his supervisor privileges himself
        # just in case of misclick
