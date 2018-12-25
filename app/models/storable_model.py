from datetime import datetime
from functools import wraps
from library.engine.errors import FieldRequired, ObjectSaveRequired
from library.engine.cache import request_time_cache
from library.engine.permissions import current_user_is_system
from copy import deepcopy


def hungarian(name):
    result = ""
    for i, l in enumerate(name):
        if 65 <= ord(l) <= 90:
            if i != 0:
                result += "_"
            result += l.lower()
        else:
            result += l
    return result


# For some reason Mongo stores datetime rounded to milliseconds
# Following is useful to avoid inconsistencies in unit tests
# - Roman Andriadi
def now():
    dt = datetime.utcnow()
    dt = dt.replace(microsecond=dt.microsecond//1000*1000)
    return dt


class ModelMeta(type):
    _collection = None

    @property
    def collection(cls):
        if cls._collection is None:
            cls._collection = hungarian(cls.__name__)
        return cls._collection


class StorableModel(object):

    __metaclass__ = ModelMeta

    FIELDS = []
    REJECTED_FIELDS = []
    REQUIRED_FIELDS = set()
    RESTRICTED_FIELDS = []
    SYSTEM_FIELDS = []
    KEY_FIELD = None
    DEFAULTS = {}
    INDEXES = []

    AUXILIARY_SLOTS = (
        "AUXILIARY_SLOTS",
        "FIELDS",
        "REJECTED_FIELDS",
        "REQUIRED_FIELDS",
        "RESTRICTED_FIELDS",
        "SYSTEM_FIELDS",
        "KEY_FIELD",
        "DEFAULTS",
        "INDEXES",
    )

    __hash__ = None

    def __init__(self, **kwargs):
        if "_id" not in kwargs:
            self._id = None
        for field, value in kwargs.iteritems():
            if field in self.FIELDS:
                setattr(self, field, value)
        self.__slots__ = []
        for field in self.FIELDS:
            if field not in kwargs:
                value = self.DEFAULTS.get(field)
                if callable(value):
                    value = value()
                elif hasattr(value, "copy"):
                    value = value.copy()
                elif hasattr(value, "__getitem__"):
                    value = value[:]
                setattr(self, field, value)
        setattr(self, '_initial_state', deepcopy(self.to_dict(self.FIELDS)))

    def save(self, skip_callback=False):
        from library.db import db
        for field in self.missing_fields:
            raise FieldRequired(field)
        if not skip_callback:
            self._before_save()
        db.save_obj(self)
        setattr(self, '_initial_state', deepcopy(self.to_dict(self.FIELDS)))
        return self

    def update(self, data, skip_callback=False):
        for field in self.FIELDS:
            if field in data and field not in self.REJECTED_FIELDS and field != "_id":
                # system fields are silently excluded if the current user is not a system user
                if field in self.SYSTEM_FIELDS and not current_user_is_system():
                    continue
                self.__setattr__(field, data[field])
        self.save(skip_callback=skip_callback)
        return self

    def destroy(self, skip_callback=False):
        from library.db import db
        if self.is_new:
            return
        if not skip_callback:
            self._before_delete()
        db.delete_obj(self)
        self._id = None
        return self

    def _before_save(self):
        pass

    def _before_delete(self):
        pass

    def __repr__(self):
        attributes = ["%s=%r" % (a, getattr(self, a))
                      for a in list(self.FIELDS)]
        return '%s(\n    %s\n)' % (self.__class__.__name__, ',\n    '.join(attributes))

    def __eq__(self, other):
        if self.__class__ != other.__class__:
            return False
        for field in self.FIELDS:
            if hasattr(self, field):
                if not hasattr(other, field):
                    return False
                if getattr(self, field) != getattr(other, field):
                    return False
            elif hasattr(other, field):
                    return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def to_dict(self, fields=None, include_restricted=False):
        if fields is None:
            fields = self.FIELDS

        # This was refactored from a list comprehension to a for-loop
        # as hasattr() catches all the exceptions in python2
        # and raising Exceptions in calculated properties don't have any effect
        #
        # For addtitional info refer to:
        # https://stackoverflow.com/questions/903130/hasattr-vs-try-except-block-to-deal-with-non-existent-attributes/16186050#16186050

        dict_data = []
        for f in fields:
            try:
                value = getattr(self, f)
            except AttributeError:
                continue
            if not (f != "_id" and f.startswith("_")) \
                    and not (f in self.AUXILIARY_SLOTS) \
                    and (include_restricted or f not in self.RESTRICTED_FIELDS) \
                    and not callable(value):
                dict_data.append((f, value))
        result = dict(dict_data)
        return result

    def reload(self):
        tmp = self.__class__.find_one({ "_id": self._id })
        for field in self.FIELDS:
            if field == "_id":
                continue
            value = getattr(tmp, field)
            setattr(self, field, value)
        return self

    @property
    def collection(self):
        return self.__class__.collection

    @property
    def is_complete(self):
        return len(self.missing_fields) == 0

    @property
    def is_new(self):
        from bson.objectid import ObjectId
        return not (hasattr(self, "_id") and type(self._id) == ObjectId)

    @property
    def missing_fields(self):
        mfields = []
        for field in self.REQUIRED_FIELDS:
            if not hasattr(self, field) or getattr(self, field) in ["", None]:
                mfields.append(field)
        return mfields

    @classmethod
    @request_time_cache()
    def find(cls, query={}, **kwargs):
        from library.db import db
        return db.get_objs(cls, cls.collection, query, **kwargs)

    @classmethod
    @request_time_cache()
    def find_one(cls, query, **kwargs):
        from library.db import db
        return db.get_obj(cls, cls.collection, query, **kwargs)

    @classmethod
    def get(cls, expression, raise_if_none=None):
        from bson.objectid import ObjectId
        from library.engine.utils import resolve_id
        expression = resolve_id(expression)
        if expression is None:
            res = None
        else:
            if type(expression) == ObjectId:
                query = {"_id": expression}
            else:
                expression = str(expression)
                query = {cls.KEY_FIELD: expression}
            res = cls.find_one(query)
        if res is None and raise_if_none is not None:
            if isinstance(raise_if_none, Exception):
                raise raise_if_none
            else:
                from library.engine.errors import NotFound
                raise NotFound(cls.__name__ + " not found")
        else:
            return res

    @classmethod
    def destroy_all(cls):
        cls.destroy_many({})

    @classmethod
    def destroy_many(cls, query):
        from library.db import db
        db.delete_query(cls.collection, query)

    @classmethod
    def ensure_indexes(cls, loud=False, overwrite=False):

        if type(cls.INDEXES) != list and type(cls.INDEXES) != tuple:
            raise TypeError("INDEXES field must be of type list or tuple")

        from pymongo import ASCENDING, DESCENDING, HASHED
        from pymongo.errors import OperationFailure
        from library.db import db
        from app import app

        def parse(key):
            if key.startswith("-"):
                key = key[1:]
                order = DESCENDING
            elif key.startswith("#"):
                key = key[1:]
                order = HASHED
            else:
                order = ASCENDING
                if key.startswith("+"):
                    key = key[1:]
            return (key, order)

        for index in cls.INDEXES:
            if type(index) == str:
                index = [index]
            keys = []
            options = { "sparse": False }

            for subindex in index:
                if type(subindex) == str:
                    keys.append(parse(subindex))
                else:
                    for key, value in subindex.items():
                        options[key] = value
            if loud:
                app.logger.debug("Creating index with options: %s, %s" % (keys, options))

            try:
                db.conn[cls.collection].create_index(keys, **options)
            except OperationFailure as e:
                if e.details.get("codeName") == "IndexOptionsConflict" or e.details.get("code") == 85:
                    if overwrite:
                        if loud:
                            app.logger.debug("Dropping index %s as conflicting" % keys)
                        db.conn[cls.collection].drop_index(keys)
                        if loud:
                            app.logger.debug("Creating index with options: %s, %s" % (keys, options))
                        db.conn[cls.collection].create_index(keys, **options)
                    else:
                        app.logger.error("Index %s conflicts with exising one, use overwrite param to fix it" % keys)

    @property
    def __dict__(self):
        return dict([x for x in self.to_dict(self.FIELDS).iteritems() if x[1] is not None])


def save_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        this = args[0]
        if this.is_new:
            raise ObjectSaveRequired("This object must be saved first")
        return func(*args, **kwargs)
    return wrapper
