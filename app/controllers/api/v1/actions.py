from app.controllers.auth_controller import AuthController
from library.engine.utils import paginated_data, json_response, resolve_id
from flask import request

actions_ctrl = AuthController("actions", __name__, require_auth=True)


@actions_ctrl.route("/", methods=["GET"])
@actions_ctrl.route("/<id>", methods=["GET"])
def index(id=None):
    from app.models import ApiAction

    if id is None:
        query = {}
        if "_users" in request.values:
            users = request.values["_users"]
            users = users.split(",")
            query["username"] = {"$in": users}
        if "_action_types" in request.values:
            action_types = request.values["_action_types"]
            action_types = action_types.split(",")
            query["action_type"] = {"$in": action_types}
        actions = ApiAction.find(query).sort([('created_at', -1)])
    else:
        action_id = resolve_id(id)
        actions = ApiAction.find({"_id": action_id})
    return json_response(paginated_data(actions))


@actions_ctrl.route("/action_types", methods=["GET"])
def action_types():
    from library.engine.action_log import action_types
    return json_response({"action_types": action_types})