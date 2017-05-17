from flask import request
from bson.objectid import ObjectId, InvalidId
from app.controllers.auth_controller import AuthController
from library.engine.utils import resolve_id, json_response, json_exception, cursor_to_list, diff

open_ctrl = AuthController("open", __name__, require_auth=False)


@open_ctrl.route("/projects2groups/<project_id>")
def projects2groups(project_id=None):
    from app.models import Project
    project_id = resolve_id(project_id)

    fields = request.values.get("fields")
    if fields is None:
        fields = ["name"]

    project = Project.find_one({"$or": [
        { "_id": project_id },
        { "name": project_id }
    ]})
    if project is None:
        return json_response({ 'errors': [ "No project found" ]}, 404)
    groups = cursor_to_list(project.groups, fields=fields)
    return json_response(groups)
