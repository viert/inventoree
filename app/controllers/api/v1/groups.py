from flask import request, g
from app.controllers.auth_controller import AuthController
from library.engine.utils import resolve_id, json_response, json_exception, paginated_data


groups_ctrl = AuthController("groups", __name__, require_auth=True)


@groups_ctrl.route("/")
@groups_ctrl.route("/<group_id>")
def show(group_id=None):
    from app.models import Group, Project
    if group_id is None:
        query = {}
        if "_filter" in request.values:
            name_filter = request.values["_filter"]
            if len(name_filter) >= 2:
                query["name"] = { "$regex": "^%s" % name_filter }
        groups = Group.find(query)
    else:
        group_id = resolve_id(group_id)
        groups = Group.find({"$or": [
            { "_id": group_id },
            { "name": group_id }
        ]})

    data = paginated_data(groups.sort("name"))
    for item in data["data"]:
        item["project_name"] = Project.find_one({ "_id": item["project_id"]}).name
    return json_response(data)

@groups_ctrl.route("/<group_id>", methods=["PUT"])
def update(group_id):
    from app.models import Group
    group_id = resolve_id(group_id)
    group = Group.find_one({
        "$or": [
            { "_id": group_id },
            { "name": group_id }
        ]
    })
    if group is None:
        return json_response({ "errors": "Group not found" }, 404)
    try:
        group.update(request.json)
    except Exception as e:
        return json_exception(e, 500)
    return json_response({ "data": group.to_dict() })

@groups_ctrl.route("/", methods=["POST"])
def create():
    from app.models import Group
    group_attrs = dict([x for x in request.json.items() if x[0] in Group.FIELDS])
    group = Group(**group_attrs)
    try:
        group.save()
    except Exception as e:
        return json_exception(e, 500)
    return json_response({ "data": group.to_dict() })

@groups_ctrl.route("/<group_id>", methods=["DELETE"])
def delete(group_id):
    from app.models import Group
    group_id = resolve_id(group_id)
    group = Group.find_one({
        "$or": [
            { "_id": group_id },
            { "name": group_id }
        ]
    })
    if group is None:
        return json_response({ "errors": "Group not found" }, 404)
    try:
        group.destroy()
    except Exception as e:
        return json_exception(e, 500)
    return json_response({ "data": group.to_dict() })
