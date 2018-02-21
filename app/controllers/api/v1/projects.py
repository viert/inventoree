from flask import request, g
from app.controllers.auth_controller import AuthController
from library.engine.utils import resolve_id, paginated_data, \
    json_response, clear_aux_fields
from library.engine.errors import ProjectNotFound, Forbidden, ApiError, UserNotFound, Conflict

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
        if projects.count() == 0:
            raise ProjectNotFound("project not found")
    return json_response(paginated_data(projects.sort("name")))


@projects_ctrl.route("/", methods=["POST"])
def create():
    from app.models import Project
    data = clear_aux_fields(request.json)
    data["owner_id"] = g.user._id
    project = Project(**data)
    project.save()
    return json_response({ "data": project.to_dict() })


@projects_ctrl.route("/<id>", methods=["PUT"])
def update(id):
    from app.models import Project
    data = clear_aux_fields(request.json)
    project = Project.get(id, ProjectNotFound("project not found"))
    if not project.modification_allowed:
        raise Forbidden("you don't have permission to modify this project")
    project.update(data)
    return json_response({"data": project.to_dict(), "status":"updated"})


@projects_ctrl.route("/<id>", methods=["DELETE"])
def delete(id):
    from app.models import Project

    project = Project.get(id, ProjectNotFound("project not found"))
    if not project.modification_allowed:
        raise Forbidden("you don't have permission to modify this project")
    project.destroy()
    return json_response({ "data": project.to_dict(), "status": "deleted" })


@projects_ctrl.route("/<id>/add_member", methods=["POST"])
def add_member(id):
    from app.models import Project, User

    project = Project.get(id, ProjectNotFound("project not found"))
    if not project.modification_allowed:
        raise Forbidden("you don't have permission to modify this project")
    if not "user_id" in request.json:
        raise ApiError("no user_id given in request payload")

    member = User.get(request.json["user_id"], UserNotFound("user not found"))
    project.add_member(member)
    return json_response({"data": project.to_dict(), "status":"updated"})


@projects_ctrl.route("/<id>/remove_member", methods=["POST"])
def remove_member(id):
    from app.models import Project, User

    project = Project.get(id, ProjectNotFound("project not found"))
    if not project.modification_allowed:
        raise Forbidden("you don't have permission to modify this project")
    if not "user_id" in request.json:
        raise ApiError("no user_id given in request payload")

    member = User.get(request.json["user_id"], UserNotFound("user not found"))
    project.remove_member(member)
    return json_response({"data": project.to_dict(), "status":"updated"})


@projects_ctrl.route("/<id>/switch_owner", methods=["POST"])
def switch_owner(id):
    from app.models import Project, User

    project = Project.get(id, ProjectNotFound("project not found"))
    if not project.member_list_modification_allowed:
        raise Forbidden("you don't have permission to modify the project's owner")
    if not "owner_id" in request.json:
        raise ApiError("you should provide owner_id field")

    user = User.get(request.json["owner_id"], UserNotFound("new owner not found"))
    if user._id == project.owner_id:
        raise Conflict("old and new owners match")

    project.owner_id = user._id
    project.save()

    return json_response({"data": project.to_dict(), "status":"updated"})

@projects_ctrl.route("/<id>/set_members", methods=["POST"])
def set_members(id):
    from app.models import Project, User
    from bson.objectid import ObjectId, InvalidId

    project = Project.get(id, ProjectNotFound("project not found"))
    if not project.member_list_modification_allowed:
        raise Forbidden("you don't have permission to modify the project's owner")
    if not "member_ids" in request.json:
        raise ApiError("you should provide member_ids field")
    if type(request.json["member_ids"]) != list:
        raise ApiError("member_ids field must be an array type")

    member_ids = [ObjectId(x) for x in request.json["member_ids"]]
    failed_ids = []
    for member_id in member_ids:
        member = User.get(member_id)
        if member is None:
            failed_ids.append(member_id)

    if len(failed_ids) > 0:
        raise UserNotFound("users with the following ids haven't been found: %s" % ", ".join([str(x) for x in failed_ids]))

    if project.owner_id in member_ids:
        member_ids.remove(project.owner_id)

    project.member_ids = member_ids
    project.save()

    return json_response({"data": project.to_dict(), "status":"updated"})
