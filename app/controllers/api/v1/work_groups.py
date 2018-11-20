from flask import request, g
from app.controllers.auth_controller import AuthController
from library.engine.utils import resolve_id, paginated_data, \
    json_response, clear_aux_fields, get_request_fields, json_body_required, filter_query
from library.engine.errors import WorkGroupNotFound, Forbidden, ApiError, UserNotFound, Conflict
from library.engine.action_log import logged_action
work_groups_ctrl = AuthController("work_groups", __name__, require_auth=True)


@work_groups_ctrl.route("/", methods=["GET"])
@work_groups_ctrl.route("/<work_group_id>", methods=["GET"])
def show(work_group_id=None):
    from app.models import WorkGroup
    if work_group_id is None:
        query = {}
        if "_filter" in request.values:
            name_filter = request.values["_filter"]
            if len(name_filter) > 0:
                query["name"] = filter_query(name_filter)
        work_groups = WorkGroup.find(query)
    else:
        work_group_id = resolve_id(work_group_id)
        work_groups = WorkGroup.find({"$or": [
            { "_id": work_group_id },
            { "name": work_group_id }
        ] })
        if work_groups.count() == 0:
            raise WorkGroupNotFound("work_group not found")
    return json_response(paginated_data(work_groups.sort("name")))


@work_groups_ctrl.route("/", methods=["POST"])
@logged_action("work_group_create")
@json_body_required
def create():
    from app.models import WorkGroup
    data = clear_aux_fields(request.json)
    data["owner_id"] = g.user._id
    work_group = WorkGroup(**data)
    work_group.save()
    return json_response({ "data": work_group.to_dict(get_request_fields()) })


@work_groups_ctrl.route("/<work_group_id>", methods=["PUT"])
@logged_action("work_group_update")
@json_body_required
def update(work_group_id):
    from app.models import WorkGroup
    data = clear_aux_fields(request.json)
    work_group = WorkGroup.get(work_group_id, WorkGroupNotFound("work_group not found"))
    if not work_group.modification_allowed:
        raise Forbidden("you don't have permission to modify this work_group")
    work_group.update(data)
    return json_response({"data": work_group.to_dict(get_request_fields()), "status":"updated"})


@work_groups_ctrl.route("/<work_group_id>", methods=["DELETE"])
@logged_action("work_group_delete")
def delete(work_group_id):
    from app.models import WorkGroup
    work_group = WorkGroup.get(work_group_id, WorkGroupNotFound("work_group not found"))
    if not work_group.member_list_modification_allowed:
        raise Forbidden("you don't have permission to modify this work_group")
    work_group.destroy()
    return json_response({ "data": work_group.to_dict(get_request_fields()), "status": "deleted" })


@work_groups_ctrl.route("/<work_group_id>/add_member", methods=["POST"])
@logged_action("work_group_add_member")
@json_body_required
def add_member(work_group_id):
    from app.models import WorkGroup, User

    work_group = WorkGroup.get(work_group_id, WorkGroupNotFound("work_group not found"))
    if not work_group.member_list_modification_allowed:
        raise Forbidden("you don't have permission to modify this work_group")
    if not "user_id" in request.json:
        raise ApiError("no user_id given in request payload")

    member = User.get(request.json["user_id"], UserNotFound("user not found"))
    work_group.add_member(member)
    return json_response({"data": work_group.to_dict(get_request_fields()), "status":"updated"})


@work_groups_ctrl.route("/<work_group_id>/remove_member", methods=["POST"])
@logged_action("work_group_remove_member")
@json_body_required
def remove_member(work_group_id):
    from app.models import WorkGroup, User

    work_group = WorkGroup.get(work_group_id, WorkGroupNotFound("work_group not found"))
    if not work_group.member_list_modification_allowed:
        raise Forbidden("you don't have permission to modify this work_group")
    if not "user_id" in request.json:
        raise ApiError("no user_id given in request payload")

    member = User.get(request.json["user_id"], UserNotFound("user not found"))
    work_group.remove_member(member)
    return json_response({"data": work_group.to_dict(get_request_fields()), "status":"updated"})


@work_groups_ctrl.route("/<work_group_id>/switch_owner", methods=["POST"])
@logged_action("work_group_switch_owner")
@json_body_required
def switch_owner(work_group_id):
    from app.models import WorkGroup, User

    work_group = WorkGroup.get(work_group_id, WorkGroupNotFound("work_group not found"))
    if not work_group.member_list_modification_allowed:
        raise Forbidden("you don't have permission to modify the work_group's owner")
    if not "owner_id" in request.json:
        raise ApiError("you should provide owner_id field")

    user = User.get(request.json["owner_id"], UserNotFound("new owner not found"))
    if user._id == work_group.owner_id:
        raise Conflict("old and new owners match")

    work_group.owner_id = user._id
    work_group.save()

    return json_response({"data": work_group.to_dict(get_request_fields()), "status":"updated"})

@work_groups_ctrl.route("/<work_group_id>/set_members", methods=["POST"])
@logged_action("work_group_set_members")
@json_body_required
def set_members(work_group_id):
    from app.models import WorkGroup, User
    from bson.objectid import ObjectId

    work_group = WorkGroup.get(work_group_id, WorkGroupNotFound("work_group not found"))
    if not work_group.member_list_modification_allowed:
        raise Forbidden("you don't have permission to modify the work_group's members")
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

    if work_group.owner_id in member_ids:
        member_ids.remove(work_group.owner_id)

    work_group.member_ids = member_ids
    work_group.save()

    return json_response({"data": work_group.to_dict(get_request_fields()), "status":"updated"})
