from datetime import datetime
from functools import wraps


def hungarian(name):
    result = ""
    for i, l in enumerate(name):
        if ord(l) >= 65 and ord(l) <= 90:
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


class ParentAlreadyExists(Exception):
    pass


class ParentCycle(Exception):
    pass


class ParentDoesNotExist(Exception):
    pass


class ChildAlreadyExists(Exception):
    pass


class ChildDoesNotExist(Exception):
    pass


class ObjectSaveRequired(Exception):
    pass


class FieldRequired(Exception):
    pass


class InvalidTags(Exception):
    pass


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
    DEFAULTS = {}
    INDEXES = []

    __hash__ = None
    __slots__ = FIELDS

    def __init__(self, **kwargs):
        if "_id" not in kwargs:
            self._id = None
        for field, value in kwargs.iteritems():
            setattr(self, field, value)
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

    def save(self, skip_callback=False):
        from library.db import db
        for field in self.missing_fields:
            raise FieldRequired(field)
        if not skip_callback:
            self._before_save()
        db.save_obj(self)

    def update(self, data, skip_callback=False):
        for field in self.FIELDS:
            if field in data and field not in self.REJECTED_FIELDS and field != "_id":
                self.__setattr__(field, data[field])
        self.save(skip_callback=skip_callback)

    def destroy(self, skip_callback=False):
        from library.db import db
        if self.is_new:
            return
        if not skip_callback:
            self._before_delete()
        db.delete_obj(self)
        delattr(self, '_id')

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

    def to_dict(self, fields=None):
        if fields is None:
            fields = self.FIELDS
        result = dict([(f, getattr(self, f)) for f in fields])
        return result

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
    def find(cls, query={}, **kwargs):
        from library.db import db
        return db.get_objs(cls, cls.collection, query, **kwargs)

    @classmethod
    def find_one(cls, query, **kwargs):
        from library.db import db
        return db.get_obj(cls, cls.collection, query, **kwargs)

    @classmethod
    def destroy_all(cls):
        # print "destroying all, class %s, collection %s" % (cls.__name__, cls.collection)
        from library.db import db
        db.delete_query(cls.collection, {})

    @classmethod
    def ensure_indexes(cls, loud=False):

        if type(cls.INDEXES) != list and type(cls.INDEXES) != tuple:
            raise TypeError("INDEXES field must be of type list or tuple")

        from pymongo import ASCENDING, DESCENDING, HASHED
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
            db.conn[cls.collection].create_index(keys, **options)


def save_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        this = args[0]
        if this.is_new:
            raise ObjectSaveRequired("This object must be saved first")
        return func(*args, **kwargs)
    return wrapper
