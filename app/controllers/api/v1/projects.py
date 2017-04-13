from flask import request
from app.controllers.auth_controller import AuthController
from library.engine.utils import resolve_id, paginated_data, \
    json_response, clear_aux_fields, json_exception

projects_ctrl = AuthController("projects", __name__, require_auth=True)

@projects_ctrl.route("/", methods=["GET"])
@projects_ctrl.route("/<id>", methods=["GET"])
def show(id=None):
    from app.models import Project
    if id is None:
        projects = Project.find()
    else:
        id = resolve_id(id)
        projects = Project.find({ "$or": [
            { "_id": id },
            { "name": id }
        ] })
    return json_response(paginated_data(projects.sort("name")))

@projects_ctrl.route("/", methods=["POST"])
def create():
    from app.models import Project
    data = clear_aux_fields(request.json)
    # TODO check user supervisor privileges
    project = Project(name=data.get("name"), email=data.get("email"), root_email=data.get("root_email"))
    try:
        project.save()
    except Exception as e:
        return json_exception(e, 500)
    return json_response({ "data": project.to_dict() })

@projects_ctrl.route("/<id>", methods=["PUT"])
def update(id):
    from app.models import Project
    data = clear_aux_fields(request.json)
    # TODO check user ownership of project
    id = resolve_id(id)
    project = Project.find_one({ "$or": [
        { "_id": id },
        { "name": id }
    ] })
    if project is None:
        return json_response({ "errors": [ "Project not found" ]}, 404)
    try:
        project.update(data)
    except Exception as e:
        return json_exception(e, 500)
    return json_response({ "data": project.to_dict(), "status": "updated" })

@projects_ctrl.route("/<id>", methods=["DELETE"])
def delete(id):
    from app.models import Project
    id = resolve_id(id)
    project = Project.find_one({ "$or": [
        { "_id": id },
        { "name": id }
    ] })
    if project is None:
        return json_response({ "errors": [ "Project not found" ]}, 404)
    # TODO check user supervisor privileges
    project.destroy()
    return json_response({ "data": project.to_dict(), "status": "deleted" })
