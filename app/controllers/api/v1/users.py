from app.controllers.auth_controller import AuthController
from flask import request, g
from library.engine.utils import json_response, resolve_id, paginated_data, get_request_fields
from library.engine.errors import UserNotFound, Forbidden, ApiError, UserAlreadyExists
from library.engine.action_log import logged_action

users_ctrl = AuthController("users", __name__, require_auth=True)


@users_ctrl.route("/")
@users_ctrl.route("/<user_id>")
def show(user_id=None):
    from app.models import User
    if user_id is None:
        query = {}
        if "_filter" in request.values:
            name_filter = request.values["_filter"]
            if len(name_filter) >= 0:
                query["username"] = { "$regex": "^%s" % name_filter }
        users = User.find(query)
    else:
        user_id = resolve_id(user_id)
        users = User.find({
            "$or": [
                { "_id": user_id },
                { "username": user_id }
            ]
        })
        if users.count() == 0:
            raise UserNotFound("user not found")

    return json_response(paginated_data(users.sort("username")))


@users_ctrl.route("/", methods=["POST"])
@logged_action("user_create")
def create():
    if not g.user.supervisor:
        raise Forbidden("you don't have permission to create new users")

    from app.models import User
    user_attrs = dict([(k, v) for k, v in request.json.items() if k in User.FIELDS])
    if "password_hash" in user_attrs:
        del(user_attrs["password_hash"])

    try:
        passwd = request.json["password_raw"]
        passwd_confirm = request.json["password_raw_confirm"]
        if passwd != passwd_confirm:
            raise ApiError("passwords don't match")
        user_attrs["password_raw"] = passwd
    except KeyError:
        pass

    existing = User.get(user_attrs["username"])
    if existing is not None:
        raise UserAlreadyExists("user with such username already exists")

    new_user = User(**user_attrs)
    new_user.save()

    return json_response({"data": new_user.to_dict(get_request_fields())})


@users_ctrl.route("/<user_id>", methods=["PUT"])
@logged_action("user_update")
def update(user_id):
    from app.models import User
    user = User.get(user_id, UserNotFound("user not found"))
    if not user.modification_allowed:
        raise Forbidden("you don't have permissions to modify this user")

    user_attrs = dict([(k, v) for k, v in request.json.items() if k in User.FIELDS])
    user.update(user_attrs)
    return json_response({"data":user.to_dict(get_request_fields())})


@users_ctrl.route("/<user_id>/set_password", methods=["PUT"])
@logged_action("user_set_password")
def set_password(user_id):
    from app.models import User
    user = User.get(user_id, UserNotFound("user not found"))
    if not user.modification_allowed:
        raise Forbidden("you don't have permissions to modify this user")

    try:
        passwd = request.json["password_raw"]
        passwd_confirm = request.json["password_raw_confirm"]
        if passwd != passwd_confirm:
            raise ApiError("passwords don't match")
    except KeyError:
        raise ApiError("you should provide password_raw and password_raw_confirm fields")

    user.set_password(passwd)
    user.save()
    return json_response({"data":user.to_dict(get_request_fields())})


@users_ctrl.route("/<user_id>/set_supervisor", methods=["PUT"])
@logged_action("user_set_supervisor")
def set_supervisor(user_id):
    from app.models import User
    user = User.get(user_id, UserNotFound("user not found"))
    if not user.supervisor_set_allowed:
        raise Forbidden("you don't have permissions to set supervisor property for this user")

    try:
        supervisor = request.json["supervisor"]
    except KeyError:
        raise ApiError("no supervisor field provided")

    if type(supervisor) != bool:
        raise ApiError("invalid superuser field type")

    user.supervisor = supervisor
    user.save()
    return json_response({"data":user.to_dict(get_request_fields())})


@users_ctrl.route("/<user_id>", methods=["DELETE"])
@logged_action("user_delete")
def delete(user_id):
    from app.models import User
    user = User.get(user_id, UserNotFound("user not found"))
    if not g.user.supervisor:
        raise Forbidden("you don't have permissions to delete this user")

    user.destroy()

    return json_response({"data":user.to_dict(get_request_fields())})
