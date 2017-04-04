from app import app
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
from bson.objectid import ObjectId, InvalidId
from time import sleep


def intercept_mongo_errors(func):
    def wrapper(*args, **kwargs):
        global __mongo_retries
        try:
            result = func(*args, **kwargs)
        except ServerSelectionTimeoutError, e:
            app.logger.error("ServerSelectionTimeout in db module")
            __mongo_retries -= 1
            if __mongo_retries == 3:
                app.logger.error("Mongo connection 3 retries passed with no result, trying to reinstall connection")
                db_obj = args[0]
                db_obj._conn = None
            if __mongo_retries == 0:
                __mongo_retries = 6
                app.logger.error("Mongo connection 3 retries more passed with no result, giving up")
                return None
            else:
                sleep(3)
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

    def init_conn(self):
        app.logger.info("Creating a new mongo connection")
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

    @intercept_mongo_errors
    def get_obj(self, cls, collection, query):
        if type(query) is not dict:
            try:
                query = { '_id': ObjectId(query) }
            except InvalidId:
                pass
        data = self.conn[collection].find_one(query)
        if data:
            return cls(**data)

    @intercept_mongo_errors
    def get_obj_id(self, collection, query):
        return self.conn[collection].find_one(query, projection=())['_id']

    @intercept_mongo_errors
    def get_objs(self, cls, collection, query, **kwargs):
        cursor = self.conn[collection].find(query, **kwargs)
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

    @intercept_mongo_errors
    def save_obj(self, obj):
        if obj.is_new:
            inserted_id = self.conn[obj.collection].insert_one(obj.to_dict()).inserted_id
            obj._id = inserted_id
        else:
            self.conn[obj.collection].replace_one({'_id': obj._id}, obj.to_dict(), upsert=True)

    @intercept_mongo_errors
    def delete_obj(self, obj):
        if obj.is_new:
            return
        self.conn[obj.collection].delete_one({'_id': obj._id})

    @intercept_mongo_errors
    def delete_query(self, collection, query):
        return self.conn[collection].delete_many(query)

    # SESSIONS

    @intercept_mongo_errors
    def get_session(self, sid, collection='sessions'):
        return self.conn[collection].find_one({ 'sid': sid })

    @intercept_mongo_errors
    def update_session(self, sid, data, expiration, collection='sessions'):
        self.conn[collection].update({ 'sid': sid }, { 'sid': sid, 'data': data, 'expiration': expiration }, True)

db = DB()