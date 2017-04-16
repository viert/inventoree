from flask import request, g
from app.controllers.auth_controller import AuthController
from library.engine.utils import resolve_id, paginated_data, \
    json_response, clear_aux_fields, json_exception

projects_ctrl = AuthController("projects", __name__, require_auth=True)

@projects_ctrl.route("/", methods=["GET"])
@projects_ctrl.route("/<project_id>", methods=["GET"])
def show(project_id=None):
    "list/show handler for projects"
    from app.models import Project
    if project_id is None:
        projects = Project.find()
    else:
        project_id = resolve_id(project_id)
        projects = Project.find({ "$or": [
            { "_id": project_id },
            { "name": project_id }
        ] })
    return json_response(paginated_data(projects.sort("name")))

@projects_ctrl.route("/", methods=["POST"])
def create():
    from app.models import Project
    data = clear_aux_fields(request.json)
    owner_id = g.user._id
    # TODO check user supervisor privileges
    project = Project(name=data.get("name"),
                      email=data.get("email"),
                      root_email=data.get("root_email"),
                      description=data.get('description'),
                      owner_id=owner_id)
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
    try:
        project.destroy()
    except Exception as e:
        return json_exception(e, 400)
    return json_response({ "data": project.to_dict(), "status": "deleted" })
