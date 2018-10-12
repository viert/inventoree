from flask import make_response, request
from bson.objectid import ObjectId, InvalidId
from collections import namedtuple
from uuid import uuid4
import flask.json as json
import os
import math

DEFAULT_DOCUMENTS_PER_PAGE = 20


class Diff(namedtuple('Diff', ('add', 'remove'))):
    pass


def json_response(data, code=200):
    from app import app
    json_kwargs = {}
    if app.config.log.get("DEBUG") or app.envtype == "development":
        json_kwargs["indent"] = 4
    return make_response(json.dumps(data, **json_kwargs), code, {'Content-Type':'application/json'})


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


def can_assign_system_fields():
    from flask import g
    try:
        # if current user is a system user, she can assign system fields
        user = g.user
        return user.system
    except AttributeError:
        # if no user is logged in, system fields are read-only as any other
        return False
    except RuntimeError:
        # if we're in shell (outside app context), we can control everything
        return True


def full_group_structure(work_group_ids=None, group_fields=None, host_fields=None):
    query = {}

    if work_group_ids is not None:
        if not hasattr(work_group_ids, '__iter__'):
            work_group_ids = [work_group_ids]
        work_group_ids = [resolve_id(x) for x in work_group_ids]
        query["work_group_id"] = { "$in": work_group_ids }

    from app.models import Group, Host
    groups = Group.find(query)
    groups = dict([(str(group._id), group.to_dict(fields=group_fields)) for group in groups])
    hosts = Host.find({})
    hosts = dict([(str(host._id), host.to_dict(fields=host_fields)) for host in hosts])

    for group in groups.values():
        group["children"] = {}
        for child_id in group["child_ids"]:
            group["children"][child_id] = groups[child_id]
        group["hosts"] = {}
        group["all_hosts"] = {}

    for host_id, host in hosts.items():
        if host["group_id"] is not None:
            groups[str(host["group_id"])]["hosts"][host_id] = host

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


def ansible_group_structure(work_group_ids=None, include_vars=True):
    from app.models import Group, Host
    query = {}
    if work_group_ids is not None:
        if not hasattr(work_group_ids, '__iter__'):
            work_group_ids = [work_group_ids]
        work_group_ids = [resolve_id(x) for x in work_group_ids]
        query["work_group_id"] = { "$in": work_group_ids }

    groups = Group.find(query).all()
    hosts = Host.find({"group_id": {"$in": [x._id for x in groups]}}).all()
    result = {}

    for group in groups:
        result[group.name] = {
            "hosts": [x.fqdn for x in group.hosts],
            "children": [x.name for x in group.children]
        }
    result["all"] = {"children": ["ungrouped"], "hosts": [x.fqdn for x in hosts]}
    result["ungrouped"] = {}
    if include_vars:
        result["_meta"] = {"hostvars": {}}
        for host in hosts:
            result["_meta"]["hostvars"][host.fqdn] = host.ansible_vars
    return result


def get_app_version():
    from app import app

    if hasattr(app, "VERSION"):
        return app.VERSION

    try:
        with open(os.path.join(app.APP_DIR, "__version__")) as vf:
            return vf.read().strip()
    except (OSError, IOError):
        return "unknown"
