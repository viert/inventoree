from app.controllers.auth_controller import AuthController
from flask import session, request, g
from library.engine.utils import json_response


account_ctrl = AuthController("auth", __name__, require_auth=False)


@account_ctrl.route("/me", methods=["GET"])
def me():
    if g.user is None:
        return json_response({ "errors": [ "You must be authenticated first" ], "state": "logged out" }, 403)
    else:
        user_data = g.user.to_dict()
        if "password_hash" in user_data:
            del(user_data["password_hash"])
        user_data["auth_token"] = g.user.get_auth_token().token
        return json_response({ "data": user_data })


@account_ctrl.route("/authenticate", methods=["POST"])
def authenticate():
    if g.user:
        user_data = g.user.to_dict()
        if "password_hash" in user_data:
            del (user_data["password_hash"])
        return json_response({ "status": "authenticated", "data": user_data })
    from app.models import User
    data = request.json
    if data is None:
        return json_response({ "errors": ["No JSON in POST data"] }, 400)
    if "username" not in data or "password" not in data:
        return json_response({ "errors": ["Insufficient fields for authenticate handler"] }, 400)
    user = User.find_one({ "username": data["username"] })
    if not user:
        return json_response({ "errors": ["Authentication error: invalid username or password"] }, 403)

    # Attention! Here follows a HACK. Supposed to be removed or at least investigated
    # why hmac requires str instead of unicode
    if not user.check_password(str(data["password"])):
        #  I meant this ^^^^^^^^^^^^^^^^^^
        return json_response({ "errors": ["Authentication error: invalid username or password"] }, 403)
    session["user_id"] = user._id
    user_data = user.to_dict()
    if "password_hash" in user_data:
        del(user_data["password_hash"])
    return json_response({ "status": "authenticated", "data": user_data })


@account_ctrl.route("/logout", methods=["POST"])
def logout():
    del(session["user_id"])
    g.user = None
    return json_response({ "status": "logged out" })