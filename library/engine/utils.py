from flask import make_response, request
from bson.objectid import ObjectId, InvalidId
import flask.json as json
import os
import math

DEFAULT_DOCUMENTS_PER_PAGE = 20


def json_response(data, code=200):
    from app import app
    json_kwargs = {}
    if app.config.log.get("DEBUG"):
        json_kwargs["indent"] = 4
    return make_response(json.dumps(data, **json_kwargs), code, {'Content-Type':'application/json'})


def json_exception(exception, code=400):
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


def cursor_to_list(crs):
    return [x.to_dict() for x in crs]


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


def paginated_data(data, page=None, limit=None):
    if "_nopaging" in request.values and request.values["_nopaging"] == "true":
        limit = None
        page = None
    else:
        if page is None:
            page = get_page()
        if limit is None:
            limit = get_limit()
    try:
        count = data.count()
        if limit is not None and page is not None:
            data = data.skip((page-1)*limit).limit(limit)
        data = cursor_to_list(data)
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