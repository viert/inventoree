from app import app
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
from bson.objectid import ObjectId, InvalidId
from time import sleep
from datetime import datetime
from random import random

MONGO_RETRIES = 6
MONGO_RETRIES_RO = 6
RETRY_SLEEP = 3 # 3 seconds

__mongo_retries = MONGO_RETRIES
__mongo_retries_ro = MONGO_RETRIES_RO


def intercept_mongo_errors_rw(func):
    def wrapper(*args, **kwargs):
        global __mongo_retries
        try:
            result = func(*args, **kwargs)
        except ServerSelectionTimeoutError:
            app.logger.error("ServerSelectionTimeout in db module for read/write operations")
            __mongo_retries -= 1
            if __mongo_retries == MONGO_RETRIES/2:
                app.logger.error("Mongo connection %d retries passed with no result, "
                                 "trying to reinstall connection" % (MONGO_RETRIES/2))
                db_obj = args[0]
                db_obj.reset_conn()
            if __mongo_retries == 0:
                __mongo_retries = MONGO_RETRIES
                app.logger.error("Mongo connection %d retries more passed with no result, giving up" % (MONGO_RETRIES/2))
                return None
            else:
                sleep(RETRY_SLEEP)
                return wrapper(*args, **kwargs)
        return result
    return wrapper


def intercept_mongo_errors_ro(func):
    def wrapper(*args, **kwargs):
        global __mongo_retries_ro
        try:
            result = func(*args, **kwargs)
        except ServerSelectionTimeoutError:
            app.logger.error("ServerSelectionTimeout in db module for read-only operations")
            __mongo_retries_ro -= 1
            if __mongo_retries_ro == MONGO_RETRIES_RO/2:
                app.logger.error("Mongo readonly connection %d retries passed, switching "
                                 "readonly operations to read-write socket" % (MONGO_RETRIES_RO/2))
                db_obj = args[0]
                db_obj._ro_conn = db_obj.conn
            if __mongo_retries_ro == 0:
                __mongo_retries_ro = MONGO_RETRIES_RO
                app.logger.error("Mongo connection %d retries more passed with no result, giving up" % (MONGO_RETRIES/2))
                return None
            else:
                sleep(RETRY_SLEEP)
                return wrapper(*args, **kwargs)
        return result
    return wrapper


class IncompleteObject(Exception):
    pass

class QueryPermissionsUpdateFailed(Exception):
    pass

class ObjectsCursor(object):

    def __init__(self, cursor, obj_class):
        self.obj_class = obj_class
        self.cursor = cursor

    def all(self):
        return list(self)

    def limit(self, *args, **kwargs):
        self.cursor.limit(*args, **kwargs)
        return self

    def skip(self, *args, **kwargs):
        self.cursor.skip(*args, **kwargs)
        return self

    def sort(self, *args, **kwargs):
        self.cursor.sort(*args, **kwargs)
        return self

    def __iter__(self):
        for item in self.cursor:
            yield self.obj_class(**item)

    def __getitem__(self, item):
        return self.obj_class(**self.cursor.__getitem__(item))

    def __getattr__(self, item):
        return getattr(self.cursor, item)


class DB(object):
    def __init__(self):
        self._conn = None
        self._ro_conn = None

    def reset_conn(self):
        self._conn = None

    def reset_ro_conn(self):
        self._ro_conn = None

    def init_ro_conn(self):
        app.logger.info("Creating a read-only mongo connection")
        client_kwargs = app.config.db.get("pymongo_extra", {})
        database = app.config.db["MONGO"]['dbname']
        if "uri_ro" in app.config.db["MONGO"]:
            ro_client = MongoClient(host=app.config.db["MONGO"]["uri_ro"], **client_kwargs)
            # AUTHENTICATION
            if 'username' in app.config.db["MONGO"] and 'password' in app.config.db["MONGO"]:
                username = app.config.db["MONGO"]["username"]
                password = app.config.db["MONGO"]['password']
                ro_client[database].authenticate(username, password)
            self._ro_conn = ro_client[database]
        else:
            app.logger.info("No uri_ro option found in configuration, falling back to read/write default connection")
            self._ro_conn = self.conn

    def init_conn(self):
        app.logger.info("Creating a read/write mongo connection")
        client_kwargs = app.config.db.get("pymongo_extra", {})
        client = MongoClient(host=app.config.db["MONGO"]["uri"], **client_kwargs)
        database = app.config.db["MONGO"]['dbname']

        # AUTHENTICATION
        if 'username' in app.config.db["MONGO"] and 'password' in app.config.db["MONGO"]:
            username = app.config.db["MONGO"]["username"]
            password = app.config.db["MONGO"]['password']
            client[database].authenticate(username, password)
        self._conn = client[database]

    @property
    def conn(self):
        if self._conn is None:
            self.init_conn()
        return self._conn

    @property
    def ro_conn(self):
        if self._ro_conn is None:
            self.init_ro_conn()
        return self._ro_conn

    @intercept_mongo_errors_ro
    def get_obj(self, cls, collection, query):
        if type(query) is not dict:
            try:
                query = { '_id': ObjectId(query) }
            except InvalidId:
                pass
        data = self.ro_conn[collection].find_one(query)
        if data:
            return cls(**data)

    @intercept_mongo_errors_ro
    def get_obj_id(self, collection, query):
        return self.ro_conn[collection].find_one(query, projection=())['_id']

    @intercept_mongo_errors_ro
    def get_objs(self, cls, collection, query, **kwargs):
        cursor = self.ro_conn[collection].find(query, **kwargs)
        return ObjectsCursor(cursor, cls)

    def get_objs_by_field_in(self, cls, collection, field, values, **kwargs):
        return self.get_objs(
            cls,
            collection,
            {
                field: {
                    '$in': values,
                },
            },
            **kwargs
        )

    @intercept_mongo_errors_rw
    def save_obj(self, obj):
        if obj.is_new:
            data = obj.to_dict(include_restricted=True)    # object to_dict() method should always return all fields
            del(data["_id"])        # although with the new object we shouldn't pass _id=null to mongo
            inserted_id = self.conn[obj.collection].insert_one(data).inserted_id
            obj._id = inserted_id
        else:
            self.conn[obj.collection].replace_one({'_id': obj._id}, obj.to_dict(include_restricted=True), upsert=True)

    @intercept_mongo_errors_rw
    def delete_obj(self, obj):
        if obj.is_new:
            return
        self.conn[obj.collection].delete_one({'_id': obj._id})

    @intercept_mongo_errors_rw
    def delete_query(self, collection, query):
        return self.conn[collection].delete_many(query)

    @intercept_mongo_errors_rw
    def update_query(self, collection, query, update):
        return self.conn[collection].update_many(query, update)

    # SESSIONS

    @intercept_mongo_errors_ro
    def get_session(self, sid, collection='sessions'):
        return self.ro_conn[collection].find_one({ 'sid': sid })

    @intercept_mongo_errors_rw
    def update_session(self, sid, data, expiration, collection='sessions'):
        self.conn[collection].update({ 'sid': sid }, { 'sid': sid, 'data': data, 'expiration': expiration }, True)
        if app.config.app.get("SESSIONS_AUTO_CLEANUP", False):
            rtrigger = app.config.app.get("SESSIONS_AUTO_CLEANUP_RAND_TRIGGER", 0.05)
            if random() < rtrigger:
                app.logger.info("Cleaning up sessions")
                self.cleanup_sessions()

    @intercept_mongo_errors_rw
    def cleanup_sessions(self, collection='sessions'):
        return self.conn[collection].remove({'expiration': {'$lt': datetime.now() }})["n"]


db = DB()
