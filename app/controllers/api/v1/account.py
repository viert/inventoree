from app.controllers.auth_controller import AuthController
from flask import session, g
from library.engine.utils import json_response
from plugins.local_authorizer import LocalAuthorizer

account_ctrl = AuthController("auth", __name__, require_auth=False)


@account_ctrl.route("/me", methods=["GET"])
def me():
    from app.models import User
    if g.user is None:
        return AuthController.error_response()
    else:
        user_data = g.user.to_dict(fields=list(User.FIELDS) + ["auth_token", "avatar"])
        return json_response({ "data": user_data })


@account_ctrl.route("/authenticate", methods=["POST"])
def authenticate():
    user_data = LocalAuthorizer.get_user_data()
    session["user_id"] = user_data["_id"]
    session.modified = True
    return json_response({ "status": "authenticated", "data": user_data })


@account_ctrl.route("/logout", methods=["POST"])
def logout():
    del(session["user_id"])
    session.modified = True
    g.user = None
    return json_response({ "status": "logged out" })
