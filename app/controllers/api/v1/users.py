from app.controllers.auth_controller import AuthController
from flask import request, g
from library.engine.utils import json_response, resolve_id, paginated_data, json_exception

users_ctrl = AuthController("users", __name__, require_auth=True)


@users_ctrl.route("/")
@users_ctrl.route("/<user_id>")
def show(user_id=None):
    from app.models import User
    if user_id is None:
        query = {}
        if "_filter" in request.values:
            name_filter = request.values["_filter"]
            if len(name_filter) >= 2:
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
            return json_response({"errors":["User not found"]}, 404)
    try:
        data = paginated_data(users.sort("username"))
    except AttributeError as e:
        return json_exception(e, 500)

    for user in data["data"]:
        if str(user["_id"]) == str(g.user._id):
            user["auth_token"] = g.user.get_auth_token().token

    return json_response(data)


@users_ctrl.route("/", methods=["POST"])
def create():
    if not g.user.supervisor:
        return json_response({"errors":["You don't have permissions to create new users"]})

    from app.models import User
    user_attrs = dict([(k, v) for k, v in request.json.items() if k in User.FIELDS])
    if "password_hash" in user_attrs:
        del(user_attrs["password_hash"])

    try:
        passwd = request.json["password_raw"]
        passwd_confirm = request.json["password_raw_confirm"]
        if passwd != passwd_confirm:
            return json_response({"errors":["Passwords don't match"]}, 400)
        user_attrs["password_raw"] = passwd
    except KeyError:
        pass

    try:
        existing = User.get(user_attrs["username"])
        if existing is not None:
            return json_response({"errors":["User with such username already exists"]}, 409)
    except KeyError:
        return json_response({"errors":["You should provide username"]}, 400)

    new_user = User(**user_attrs)
    try:
        new_user.save()
    except Exception as e:
        return json_exception(e, 500)

    return json_response({"data": new_user.to_dict()})


@users_ctrl.route("/<user_id>", methods=["PUT"])
def update(user_id):
    from app.models import User
    user = User.get(user_id)
    if user is None:
        return json_response({"errors":["User not found"]}, 404)
    if not user.modification_allowed:
        return json_response({"errors":["You don't have permissions to modificate this user"]}, 403)

    user_attrs = dict([(k, v) for k, v in request.json.items() if k in User.FIELDS])
    try:
        user.update(user_attrs)
    except Exception as e:
        return json_exception(e, 500)

    return json_response({"data":user.to_dict()})


@users_ctrl.route("/<user_id>/set_password", methods=["PUT"])
def set_password(user_id):
    from app.models import User
    user = User.get(user_id)
    if user is None:
        return json_response({"errors":["User not found"]}, 404)
    if not user.modification_allowed:
        return json_response({"errors":["You don't have permissions to modificate this user"]}, 403)


    try:
        passwd = request.json["password_raw"]
        passwd_confirm = request.json["password_raw_confirm"]
        if passwd != passwd_confirm:
            return json_response({"errors":["Passwords don't match"]}, 400)
    except KeyError:
        return json_response({"errors":["You should provide password_raw and password_raw_confirm fields"]}, 400)

    user.set_password(passwd)
    user.save()
    return json_response({"data":user.to_dict()})


@users_ctrl.route("/<user_id>/set_supervisor", methods=["PUT"])
def set_supervisor(user_id):
    from app.models import User
    user = User.get(user_id)

    if user is None:
        return json_response({"errors":["User not found"]}, 404)
    if not user.supervisor_set_allowed:
        return json_response({"errors":["You don't have permissions to set supervisor property for this user"]}, 403)

    try:
        supervisor = request.json["supervisor"]
    except KeyError:
        return json_response({"errors":["No supervisor field provided"]}, 400)

    if type(supervisor) != bool:
        return json_response({"errors":["Invalid superuser field type"]}, 400)

    user.supervisor = supervisor
    user.save()

    return json_response({"data":user.to_dict()})


@users_ctrl.route("/<user_id>", methods=["DELETE"])
def delete(user_id):
    from app.models import User
    user = User.get(user_id)

    if user is None:
        return json_response({"errors":["User not found"]}, 404)
    if not g.user.supervisor:
        return json_response({"errors":["You don't have permissions to delete this user"]}, 403)

    try:
        user.destroy()
    except Exception as e:
        return json_exception(e, 500)

    return json_response({"data":user.to_dict()})
