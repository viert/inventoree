from app.controllers.auth_controller import AuthController
from flask import session, request, g
from library.engine.utils import json_response


account_ctrl = AuthController("auth", __name__, require_auth=False)


@account_ctrl.route("/authenticate", methods=["POST"])
def authenticate():
    if g.user:
        return json_response({ "errors": ["Already authenticated. Use /api/v1/account/logout handler first"]}, 400)
    from app.models import User
    data = request.json
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
    return json_response({ "status": "authenticated" }, 200)


@account_ctrl.route("/logout", methods=["POST"])
def logout():
    del(session["user_id"])
    g.user = None
    return json_response({ "status": "logged out" })