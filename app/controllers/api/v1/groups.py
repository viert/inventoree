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
    if not group.modification_allowed:
        return json_response({ "errors": ["You don't have permissions to modify this group"]}, 403)
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
    if not group.modification_allowed:
        return json_response({ "errors": ["You don't have permissions to modify this group"]}, 403)
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
    if not group.modification_allowed:
        return json_response({ "errors": ["You don't have permissions to modify this group"]}, 403)
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
    from app.models import Group, Project

    group_attrs = request.json.copy()
    if "project_id" not in group_attrs:
        if "project_name" in group_attrs:
            project = Project.find_one({ "name": group_attrs["project_name"] })
            if project is not None:
                group_attrs["project_id"] = project._id
                del(group_attrs["project_name"])
            else:
                return json_response({"errors": ["Project provided has not been found"]}, 404)
        else:
            return json_response({"errors": ["No project provided for the group"]}, 400)
    else:
        try:
            group_attrs["project_id"] = ObjectId(group_attrs["project_id"])
        except InvalidId:
            return json_response({"errors": ["Invalid project_id provided"]}, 400)
        project = Project.find_one({ "_id": group_attrs["project_id"]})
        if project is None:
            return json_response({ "errors": ["Project provided has not been found"]}, 404)

    group_attrs = dict([x for x in group_attrs.items() if x[0] in Group.FIELDS])
    if not project.modification_allowed:
        return json_response({ "errors": ["You don't have permissions to create groups in this project"]}, 403)
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
    if not group.modification_allowed:
        return json_response({ "errors": ["You don't have permissions to modify this group"]}, 403)
    try:
        group.destroy()
    except Exception as e:
        return json_exception(e, 500)
    return json_response({ "data": group.to_dict() })

@groups_ctrl.route("/mass_move", methods=["POST"])
def mass_move():
    # every group requested will move to the indicated project with all its' children
    # group will be detached from all its' parents due to not being able to have
    # relations between different projects

    if "project_id" not in request.json or request.json["project_id"] is None:
        return json_response({ "errors": ["No project provided to move to"] }, 400)
    if "group_ids" not in request.json or request.json["group_ids"] is None:
        return json_response({ "errors": ["No group ids provided"]}, 400)
    if type(request.json["group_ids"]) != list:
        return json_response({ "errors": ["group_ids must be an array type"]}, 400)

    from app.models import Group, Project

    # resolving Project
    project_id = resolve_id(request.json["project_id"])
    project = Project.find_one({ "_id": project_id })
    if project is None:
        return json_response({ "errors": ["Project not found"]}, 404)

    # resolving Groups and their children
    group_ids = [resolve_id(x) for x in request.json["group_ids"]]
    group_ids = set([x for x in group_ids if x is not None])
    groups = Group.find({ "_id": { "$in": list(group_ids) }})
    groups = [g for g in groups if g is not None and g.project_id != project._id] # don't affect groups already in the project

    if len(groups) == 0:
        return json_response({ "errors": ["No groups found to be moved"]}, 404)

    all_groups = set()
    for group in groups:
        all_groups.add(group)
        for child in group.get_all_children():
            all_groups.add(child)

    # detaching high level groups from parents
    for group in groups:
        group.remove_all_parents()

    # moving all groups and their children to the new project
    for group in all_groups:
        group.project_id = project._id
        group.save(skip_callback=True)

    result = {
        "status": "ok",
        "data": {
            "project": project.to_dict(),
            "groups": [x.to_dict() for x in all_groups]
        }
    }

    return json_response(result)