from flask import request, g
from app.controllers.auth_controller import AuthController
from library.engine.utils import resolve_id, json_response, paginated_data

groups_ctrl = AuthController("groups", __name__, require_auth=True)


@groups_ctrl.route("/")
@groups_ctrl.route("/<group_id>")
def show(group_id=None):
    from app.models import Group
    if group_id is None:
        groups = Group.find()
    else:
        group_id = resolve_id(group_id)
        groups = Group.find({"$or": [
            { "_id": group_id },
            { "name": group_id }
        ]})
    return json_response(paginated_data(groups.sort("name")))