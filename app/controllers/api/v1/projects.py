from flask import request, g
from app.controllers.auth_controller import AuthController
from library.engine.utils import resolve_id, paginated_data, \
    json_response, clear_aux_fields, get_request_fields
from library.engine.errors import ProjectNotFound, Forbidden, ApiError, UserNotFound, Conflict
from library.engine.action_log import logged_action
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
@logged_action("project_create")
def create():
    from app.models import Project
    data = clear_aux_fields(request.json)
    data["owner_id"] = g.user._id
    project = Project(**data)
    project.save()
    return json_response({ "data": project.to_dict(get_request_fields()) })


@projects_ctrl.route("/<project_id>", methods=["PUT"])
@logged_action("project_update")
def update(project_id):
    from app.models import Project
    data = clear_aux_fields(request.json)
    project = Project.get(project_id, ProjectNotFound("project not found"))
    if not project.modification_allowed:
        raise Forbidden("you don't have permission to modify this project")
    project.update(data)
    return json_response({"data": project.to_dict(get_request_fields()), "status":"updated"})


@projects_ctrl.route("/<project_id>", methods=["DELETE"])
@logged_action("project_delete")
def delete(project_id):
    from app.models import Project

    project = Project.get(project_id, ProjectNotFound("project not found"))
    if not project.member_list_modification_allowed:
        raise Forbidden("you don't have permission to modify this project")
    project.destroy()
    return json_response({ "data": project.to_dict(get_request_fields()), "status": "deleted" })


@projects_ctrl.route("/<project_id>/add_member", methods=["POST"])
@logged_action("project_add_member")
def add_member(project_id):
    from app.models import Project, User

    project = Project.get(project_id, ProjectNotFound("project not found"))
    if not project.member_list_modification_allowed:
        raise Forbidden("you don't have permission to modify this project")
    if not "user_id" in request.json:
        raise ApiError("no user_id given in request payload")

    member = User.get(request.json["user_id"], UserNotFound("user not found"))
    project.add_member(member)
    return json_response({"data": project.to_dict(get_request_fields()), "status":"updated"})


@projects_ctrl.route("/<project_id>/remove_member", methods=["POST"])
@logged_action("project_remove_member")
def remove_member(project_id):
    from app.models import Project, User

    project = Project.get(project_id, ProjectNotFound("project not found"))
    if not project.member_list_modification_allowed:
        raise Forbidden("you don't have permission to modify this project")
    if not "user_id" in request.json:
        raise ApiError("no user_id given in request payload")

    member = User.get(request.json["user_id"], UserNotFound("user not found"))
    project.remove_member(member)
    return json_response({"data": project.to_dict(get_request_fields()), "status":"updated"})


@projects_ctrl.route("/<project_id>/switch_owner", methods=["POST"])
@logged_action("project_switch_owner")
def switch_owner(project_id):
    from app.models import Project, User

    project = Project.get(project_id, ProjectNotFound("project not found"))
    if not project.member_list_modification_allowed:
        raise Forbidden("you don't have permission to modify the project's owner")
    if not "owner_id" in request.json:
        raise ApiError("you should provide owner_id field")

    user = User.get(request.json["owner_id"], UserNotFound("new owner not found"))
    if user._id == project.owner_id:
        raise Conflict("old and new owners match")

    project.owner_id = user._id
    project.save()

    return json_response({"data": project.to_dict(get_request_fields()), "status":"updated"})

@projects_ctrl.route("/<project_id>/set_members", methods=["POST"])
@logged_action("project_set_members")
def set_members(project_id):
    from app.models import Project, User
    from bson.objectid import ObjectId

    project = Project.get(project_id, ProjectNotFound("project not found"))
    if not project.member_list_modification_allowed:
        raise Forbidden("you don't have permission to modify the project's members")
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

    return json_response({"data": project.to_dict(get_request_fields()), "status":"updated"})
