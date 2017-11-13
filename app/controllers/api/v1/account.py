from app.controllers.auth_controller import AuthController, AuthenticationError
from flask import session, g
from library.engine.utils import json_response
from plugins.local_authorizer import LocalAuthorizer

account_ctrl = AuthController("auth", __name__, require_auth=False)


@account_ctrl.route("/me", methods=["GET"])
def me():
    if g.user is None:
        return AuthController.error_response()
    else:
        user_data = g.user.to_dict()
        user_data["auth_token"] = g.user.get_auth_token().token
        return json_response({ "data": user_data })


@account_ctrl.route("/authenticate", methods=["POST"])
def authenticate():
    try:
        user_data = LocalAuthorizer.get_user_data()
    except AuthenticationError as ae:
        return json_response({ "errors": ["Authentication Error: %s" % ae.message] }, ae.code)
    session["user_id"] = user_data["_id"]
    return json_response({ "status": "authenticated", "data": user_data })


@account_ctrl.route("/logout", methods=["POST"])
def logout():
    del(session["user_id"])
    g.user = None
    return json_response({ "status": "logged out" })