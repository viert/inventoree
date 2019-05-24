from storable_model import StorableModel, now
from library.engine.pbkdf2 import pbkdf2_hex
from library.engine.permissions import get_user_from_app_context
from library.engine.cache import request_time_cache
from library.engine.errors import InvalidPassword, InvalidDocumentsPerPage
from time import mktime
from flask import g, has_request_context
import bcrypt


class UserIsInWorkGroups(Exception):
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
        "system",
        "custom_data",
        "documents_per_page",
    )

    KEY_FIELD = "username"

    DEFAULTS = {
        "first_name": "",
        "last_name": "",
        "avatar_url": "",
        "password_hash": "-",
        "email": "",
        "custom_data": {},
        "ext_id": None,
        "supervisor": False,
        "system": False,
        "documents_per_page": 20
    }

    RESTRICTED_FIELDS = [
        "password_hash",
        "salt"
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
        "system",
    )

    INDEXES = (
        ["username",{"unique": True}],
        "ext_id",
        "custom_data",
        "supervisor",
        "system",
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
        if not isinstance(self.documents_per_page, int):
            raise InvalidDocumentsPerPage("documents_per_page must be int")
        self.touch()

    def _before_delete(self):
        if self.work_groups_owned.count() > 0:
            raise UserIsInWorkGroups("Can't remove user with work_groups owned by")
        for work_group in self.work_groups_included_into:
            work_group.remove_member(self)

    def set_password(self, password_raw):
        if password_raw == "":
            raise InvalidPassword("Password can not be empty")
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
        if not has_request_context():
            return self.token_class.find({"user_id": self._id})
        else:
            current_user = g.user
            if current_user and (current_user.supervisor or current_user._id == self._id):
                return self.token_class.find({"user_id": self._id})
        return []

    @property
    def avatar(self):
        if self.avatar_url:
            return self.avatar_url
        if not self.email:
            return ""

        from hashlib import md5
        from app import app
        gravatar_path = app.config.app.get("GRAVATAR_PATH")
        if not gravatar_path:
            return ""
        gravatar_hash = md5(self.email.strip()).hexdigest()
        return "%s/%s.jpg" % (gravatar_path, gravatar_hash)

    def get_auth_token(self):
        tokens = self.token_class.find({"type": "auth", "user_id": self._id})
        suitable_token = None
        for token in tokens:
            if token.expired():
                token.destroy()
            elif token.close_to_expiration():
                continue
            else:
                suitable_token = token
        if suitable_token is None:
            suitable_token = self.token_class(type="auth", user_id=self._id)
            suitable_token.save()
        return suitable_token

    @property
    def auth_token(self):
        if has_request_context():
            current_user = g.user
            if not current_user:
                return None
            if not current_user.supervisor and not current_user._id == self._id:
                return None
        return self.get_auth_token().token

    @property
    @request_time_cache()
    def work_groups_owned(self):
        from app.models import WorkGroup
        return WorkGroup.find({"owner_id": self._id})

    @property
    @request_time_cache()
    def work_groups_included_into(self):
        from app.models import WorkGroup
        return WorkGroup.find({"member_ids": self._id})

    @property
    def member_of(self):
        from app.models import WorkGroup
        return WorkGroup.find({"$or":[
            {"member_ids": self._id},
            {"owner_id": self._id}
        ]})

    @property
    def modification_allowed(self):
        user = get_user_from_app_context()
        if user is None: return False
        if user.supervisor or self._id == user._id: return True
        return False

    @property
    def system_set_allowed(self):
        return self.supervisor_set_allowed

    @property
    def supervisor_set_allowed(self):
        # user can't revoke his supervisor privileges himself
        # just in case of misclick
        user = get_user_from_app_context()
        return user.supervisor and user._id != self._id
