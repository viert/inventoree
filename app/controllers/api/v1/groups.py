from flask import request
from bson.objectid import ObjectId, InvalidId
from app.controllers.auth_controller import AuthController
from library.engine.utils import resolve_id, json_response, json_exception, paginated_data, diff

groups_ctrl = AuthController("groups", __name__, require_auth=True)


def _get_group_by_id(group_id):
    from app.models import Group
    group_id = resolve_id(group_id)
    return Group.find_one({
        "$or": [
            { "_id": group_id },
            { "name": group_id }
        ]
    })


@groups_ctrl.route("/")
@groups_ctrl.route("/<group_id>")
def show(group_id=None):
    from app.models import Group
    if group_id is None:
        query = {}
        if "_filter" in request.values:
            name_filter = request.values["_filter"]
            if len(name_filter) >= 2:
                query["name"] = { "$regex": "^%s" % name_filter }
        if "project_id" in request.values:
            project_id = resolve_id(request.values["project_id"])
            query["project_id"] = project_id
        groups = Group.find(query)
    else:
        group_id = resolve_id(group_id)
        groups = Group.find({"$or": [
            { "_id": group_id },
            { "name": group_id }
        ]})

    data = paginated_data(groups.sort("name"))
    return json_response(data)

@groups_ctrl.route("/<group_id>", methods=["PUT"])
def update(group_id):
    group = _get_group_by_id(group_id)
    if group is None:
        return json_response({ "errors": ["Group not found"] }, 404)
    # TODO: check permissions!
    try:
        group.update(request.json)
    except Exception as e:
        return json_exception(e, 500)
    if "_fields" in request.values:
        fields = request.values["_fields"].split(",")
    else:
        fields = None
    return json_response({ "data": group.to_dict(fields) })

@groups_ctrl.route("/<group_id>/set_children", methods=["PUT"])
def set_children(group_id):
    group = _get_group_by_id(group_id)
    if group is None:
        return json_response({ "errors": ["Group not found"] }, 404)
    # TODO: check permissions!
    orig = group.child_ids
    upd = request.json["child_ids"]
    try:
        upd = [ObjectId(x) for x in upd]
    except InvalidId as e:
        return json_exception(e, 400)
    d =  diff(orig, upd)
    exs = []
    for item in d.remove:
        try:
            group.remove_child(item)
        except Exception as e:
            exs.append(e)
    for item in d.add:
        try:
            group.add_child(item)
        except Exception as e:
            exs.append(e)
    if len(exs) > 0:
        return json_response({ "errors": ["%s: %s" % (x.__class__.__name__, x.message) for x in exs] }, 400)
    else:
        if "_fields" in request.values:
            fields = request.values["_fields"].split(",")
        else:
            fields = None
        return json_response({ "data": group.to_dict(fields), "status": "ok" })

@groups_ctrl.route("/<group_id>/set_hosts", methods=["PUT"])
def set_hosts(group_id):
    from app.models import Host
    group = _get_group_by_id(group_id)
    if group is None:
        return json_response({ "errors": ["Group not found"] }, 404)
    # TODO: check permissions!
    orig = group.host_ids
    upd = request.json["host_ids"]
    try:
        upd = [ObjectId(x) for x in upd]
    except InvalidId as e:
        return json_exception(e, 400)
    d =  diff(orig, upd)
    exs = []
    for item in d.remove:
        try:
            h = Host.find_one({ "_id": item })
            if h is not None:
                h.group_id = None
                h.save()
        except Exception as e:
            exs.append(e)
    for item in d.add:
        try:
            h = Host.find_one({ "_id": item })
            if h is not None:
                h.group_id = group._id
                h.save()
        except Exception as e:
            exs.append(e)
    if len(exs) > 0:
        return json_response({ "errors": ["%s: %s" % (x.__class__.__name__, x.message) for x in exs] }, 400)
    else:
        if "_fields" in request.values:
            fields = request.values["_fields"].split(",")
        else:
            fields = None
        return json_response({ "data": group.to_dict(fields), "status": "ok" })


@groups_ctrl.route("/", methods=["POST"])
def create():
    from app.models import Group
    group_attrs = dict([x for x in request.json.items() if x[0] in Group.FIELDS])
    if "project_id" not in group_attrs or group_attrs["project_id"] is None:
        return json_response({ "errors": [ "No project provided for the group" ] }, 400)
    try:
        group_attrs["project_id"] = ObjectId(group_attrs["project_id"])
    except InvalidId as e:
        return json_response({ "errors": [ "Invalid project_id provided" ] }, 400)
    # TODO: check permissions!
    group = Group(**group_attrs)
    try:
        group.save()
    except Exception as e:
        return json_exception(e, 500)
    if "_fields" in request.values:
        fields = request.values["_fields"].split(",")
    else:
        fields = None
    return json_response({ "data": group.to_dict(fields) }, 201)

@groups_ctrl.route("/<group_id>", methods=["DELETE"])
def delete(group_id):
    group = _get_group_by_id(group_id)
    if group is None:
        return json_response({ "errors": ["Group not found"] }, 404)
    # TODO: check permissions!
    try:
        group.destroy()
    except Exception as e:
        return json_exception(e, 500)
    return json_response({ "data": group.to_dict() })
