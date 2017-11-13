from app.controllers.auth_controller import AuthController, AuthenticationError
from flask import session, request, g
from library.engine.utils import json_response

account_ctrl = AuthController("auth", __name__, require_auth=False)


@account_ctrl.route("/me", methods=["GET"])
def me():
    if g.user is None:
        return json_response({ "errors": [ "You must be authenticated first" ], "state": "logged out" }, 403)
    else:
        user_data = g.user.to_dict()
        user_data["auth_token"] = g.user.get_auth_token().token
        return json_response({ "data": user_data })


@account_ctrl.route("/authenticate", methods=["POST"])
def authenticate():
    from app import app
    try:
        user_data = app.authorizer.get_user_data()
    except AuthenticationError as ae:
        return json_response({ "errors": ["Authentication Error: %s" % ae.message] }, ae.code)
    session["user_id"] = user_data["_id"]
    return json_response({ "status": "authenticated", "data": user_data })


@account_ctrl.route("/logout", methods=["POST"])
def logout():
    del(session["user_id"])
    g.user = None
    return json_response({ "status": "logged out" })