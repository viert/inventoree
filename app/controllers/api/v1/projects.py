from flask import request, g
from app.controllers.auth_controller import AuthController
from library.engine.utils import resolve_id, paginated_data, \
    json_response, clear_aux_fields, json_exception

projects_ctrl = AuthController("projects", __name__, require_auth=True)


@projects_ctrl.route("/", methods=["GET"])
@projects_ctrl.route("/<project_id>", methods=["GET"])
def show(project_id=None):
    from app.models import Project
    if project_id is None:
        query = {}
        if "_filter" in request.values:
            name_filter = request.values["_filter"]
            if len(name_filter) > 2:
                query["name"] = { "$regex": "^%s" % name_filter }
        projects = Project.find(query)
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
    id = resolve_id(id)
    project = Project.find_one({"$or": [
        {"_id": id},
        {"name": id}
    ]})
    if project is None:
        return json_response({ "errors": [ "Project not found" ]}, 404)
    if not project.modification_allowed:
        return json_response({"errors": ["You don't have permissions to modify the project"]}, 403)
    try:
        project.update(data)
    except Exception as e:
        return json_exception(e, 500)
    return json_response({ "data": project.to_dict(), "status": "updated" })


@projects_ctrl.route("/<id>", methods=["DELETE"])
def delete(id):
    from app.models import Project
    id = resolve_id(id)
    project = Project.find_one({"$or": [
        {"_id": id},
        {"name": id}
    ]})
    if project is None:
        return json_response({ "errors": [ "Project not found" ]}, 404)
    if not project.modification_allowed:
        return json_response({ "errors": [ "You don't have permissions to modify the project" ]}, 403)
    try:
        project.destroy()
    except Exception as e:
        return json_exception(e, 400)
    return json_response({ "data": project.to_dict(), "status": "deleted" })


@projects_ctrl.route("/<id>/add_member", methods=["POST"])
def add_member(id):
    from app.models import Project, User
    id = resolve_id(id)
    project = Project.find_one({"$or": [
        {"_id": id},
        {"name": id}
    ]})
    if project is None:
        return json_response({ "errors": [ "Project not found" ]}, 404)
    if not project.member_list_modification_allowed:
        return json_response({ "errors": [ "You don't have permissions to modify the project" ]}, 403)

    if not "_id" in request.json:
        return json_response({ "errors": [ "No user id given in request data"]}, 400)

    member = User.find_one({"_id": request.json["_id"]})
    if member is None:
        return json_response({ "errors": ["User not found"]}, 404)

    project.member_ids.append(member._id)
    project.save()
    return json_response({"data": project.to_dict()})


@projects_ctrl.route("/<id>/remove_member", methods=["POST"])
def remove_member(id):
    from app.models import Project
    id = resolve_id(id)
    project = Project.find_one({"$or": [
        {"_id": id},
        {"name": id}
    ]})
    if project is None:
        return json_response({ "errors": [ "Project not found" ]}, 404)
    if not project.member_list_modification_allowed:
        return json_response({ "errors": [ "You don't have permissions to modify the project" ]}, 403)

    if not "_id" in request.json:
        return json_response({ "errors": [ "No user id given in request data"]}, 400)

    if request.json["_id"] not in project.member_ids:
        return json_response({ "errors": [ "Member not found" ]}, 404)

    project.member_ids.remove(request.json["_id"])
    project.save()
    return json_response({"data": project.to_dict()})
