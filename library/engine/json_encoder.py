from bson.objectid import ObjectId
from flask.json import JSONEncoder


class MongoJSONEncoder(JSONEncoder):
    def default(self, o):
        from app.models.storable_model import StorableModel
        from library.db import ObjectsCursor
        if isinstance(o, ObjectId):
            return str(o)
        elif isinstance(o, ObjectsCursor) or isinstance(o, set):
            return list(o)
        elif isinstance(o, StorableModel):
            return o.to_dict()
        else:
            return JSONEncoder.default(self, o)