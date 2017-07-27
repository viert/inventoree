from flask import make_response, request
from bson.objectid import ObjectId, InvalidId
from collections import namedtuple
from uuid import uuid4
import flask.json as json
import os
import math
import traceback

DEFAULT_DOCUMENTS_PER_PAGE = 20


class Diff(namedtuple('Diff', ('add', 'remove'))):
    pass


def json_response(data, code=200):
    from app import app
    json_kwargs = {}
    if app.config.log.get("DEBUG"):
        json_kwargs["indent"] = 4
    return make_response(json.dumps(data, **json_kwargs), code, {'Content-Type':'application/json'})


def json_exception(exception, code=400):
    from app import app
    from sys import exc_info
    exc_type, exc_value, exc_traceback = exc_info()
    app.logger.error("\n" + "\n".join(traceback.format_exception(exc_type, exc_value, exc_traceback)))
    errors = [ "%s: %s" % (exception.__class__.__name__, exception.message) ]
    return make_response(json.dumps({'errors': errors}), code, {'Content-Type':'application/json'})


def get_py_files(directory):
    return [f for f in os.listdir(directory) if f.endswith(".py")]


def get_modules(directory):
    return [x[:-3] for x in get_py_files(directory) if x != "__init__.py"]


def resolve_id(id):
    try:
        id = ObjectId(id)
    except InvalidId:
        pass
    return id


def cursor_to_list(crs, fields=None):
    return [x.to_dict(fields) for x in crs]


def get_page():
    if '_page' in request.values:
        page = request.values['_page']
    else:
        page = 1
    try:
        page = int(page)
    except (TypeError, ValueError):
        page = 1
    return page


def get_limit():
    from app import app
    default_limit = app.config.app.get('DOCUMENTS_PER_PAGE', DEFAULT_DOCUMENTS_PER_PAGE)
    if '_limit' in request.values:
        limit = request.values['_limit']
        try:
            limit = int(limit)
        except:
            limit = default_limit
    else:
        limit = default_limit
    return limit


def paginated_data(data, page=None, limit=None, fields=None):
    if "_nopaging" in request.values and request.values["_nopaging"] == "true":
        limit = None
        page = None
    else:
        if page is None:
            page = get_page()
        if limit is None:
            limit = get_limit()

    if "_fields" in request.values:
        fields = request.values["_fields"].split(",")

    try:
        count = data.count()
        if limit is not None and page is not None:
            data = data.skip((page-1)*limit).limit(limit)
        data = cursor_to_list(data, fields=fields)
    except AttributeError:
        count = len(data)
        data = data[(page-1)*limit:page*limit]

    total_pages = int(math.ceil(float(count) / limit)) if limit is not None else None

    return {
        "page": page,
        "total_pages": total_pages,
        "count": count,
        "data": data
    }


def clear_aux_fields(data):
    return dict([(k, v) for k, v in data.iteritems() if not k.startswith("_")])


def diff(original, updated):
    o = set(original)
    u = set(updated)
    add = [x for x in u if x not in o]
    remove = [x for x in o if x not in u]
    return Diff(add=add, remove=remove)


def uuid4_string():
    return str(uuid4())


def get_user_from_app_context():
    from app import app
    from flask import g
    user = None
    try:
        with app.flask.app_context():
            user = g.user
    except AttributeError:
        pass
    return user
