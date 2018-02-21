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
    # ObjectId(None) apparently generates a new unique object id
    # which is not a behaviour we need
    if id is None:
        return None

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


def get_request_fields():
    try:
        if "_fields" in request.values:
            return request.values["_fields"].split(",")
        else:
            return None
    except RuntimeError:
        return None


def paginated_data(data, page=None, limit=None, fields=None, extra=None):
    from app.models.storable_model import StorableModel
    if "_nopaging" in request.values and request.values["_nopaging"] == "true":
        limit = None
        page = None
    else:
        if page is None:
            page = get_page()
        if limit is None:
            limit = get_limit()

    if fields is None:
        fields = get_request_fields()

    if type(data) == list:
        count = len(data)
        data = data[(page - 1) * limit:page * limit]
        data = [x.to_dict(fields=fields) for x in data if isinstance(x, StorableModel)]
    elif hasattr(data, "count"):
        count = data.count()
        if limit is not None and page is not None:
            data = data.skip((page-1)*limit).limit(limit)
        data = cursor_to_list(data, fields=fields)
    else:
        raise RuntimeError("paginated_data accepts either cursor objects or lists")

    total_pages = int(math.ceil(float(count) / limit)) if limit is not None else None

    result = {
        "page": page,
        "total_pages": total_pages,
        "count": count,
        "data": data
    }

    if extra is not None and hasattr(extra, "items"):   # extra type checking
        for k, v in extra.items():
            if k not in result:                         # no overriding
                result[k]= v

    return result


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
    from flask import g
    user = None
    try:
        user = g.user
    except AttributeError:
        pass
    return user


def full_group_structure(project_ids=None):
    query = {}

    if project_ids is not None:
        if not hasattr(project_ids, '__iter__'):
            project_ids = [project_ids]
        project_ids = [resolve_id(x) for x in project_ids]
        query["project_id"] = { "$in": project_ids }

    from app.models import Group, Host
    groups = Group.find(query)
    groups = dict([(group._id, group.to_dict()) for group in groups])
    hosts = Host.find({})
    hosts = dict([(host._id, host.to_dict()) for host in hosts])

    for group in groups.values():
        group["children"] = {}
        for child_id in group["child_ids"]:
            group["children"][child_id] = groups[child_id]
        group["hosts"] = {}
        group["all_hosts"] = {}

    for host_id, host in hosts.items():
        groups[host["group_id"]]["hosts"][host_id] = host

    def get_all_hosts(group):
        hosts = {}
        for k, v in group["hosts"].items():
            hosts[k] = v
        for child in group["children"].values():
            for k, v in get_all_hosts(child).items():
                hosts[k] = v
        return hosts

    for group in groups.values():
        group["all_hosts"] = get_all_hosts(group)

    return groups
