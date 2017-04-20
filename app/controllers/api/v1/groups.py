from flask import request, g
from app.controllers.auth_controller import AuthController
from library.engine.utils import resolve_id, json_response, paginated_data


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
            else:
                query["name"] = None
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