from app.controllers.auth_controller import AuthController
from library.engine.utils import paginated_data, json_response
from flask import request

actions_ctrl = AuthController("actions", __name__, require_auth=True)

@actions_ctrl.route("/", methods=["GET"])
def index():
    from app.models import ApiAction
    query = {}
    if "_username_filter" in request.values:
        username_filter = request.values["_username_filter"]
        if len(username_filter) > 2:
            query["username"] = {"$regex": "^%s" % username_filter}
    if "_action_type_filter" in request.values:
        actiontype_filter = request.values["_action_type_filter"]
        if len(actiontype_filter) > 2:
            query["action_type"] = {"$regex": "^%s" % actiontype_filter}

    actions = ApiAction.find(query).sort([('created_at', -1)])
    return json_response(paginated_data(actions))
