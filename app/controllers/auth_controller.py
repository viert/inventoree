from flask import Blueprint, g, session, request
from library.engine.utils import json_response

class AuthController(Blueprint):
    def __init__(self, *args, **kwargs):
        self.require_auth = kwargs.get("require_auth") or False
        if "require_auth" in kwargs:
            del(kwargs["require_auth"])
        Blueprint.__init__(self, *args, **kwargs)
        self.before_request(self.set_current_user)

    def set_current_user(self):
        from app.models import User
        g.user = None

        if "Authorization" in request.headers:
            auth = request.headers["Authorization"].split()
            if len(auth) == 2 and auth[0] == "Token":
                from app.models import Token
                token = Token.find_one({ "token": auth[1] })
                if token is not None and not token.expired:
                    g.user = token.user

        if g.user is None:
            user_id = session.get("user_id")
            if user_id:
                user = User.find_one({ "_id": user_id })
                if user:
                    g.user = user

        if g.user is None and self.require_auth:
            return json_response({ "errors": [ "You must be authenticated first" ], "state": "logged out" }, 403)