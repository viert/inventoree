from flask import Blueprint, g, session
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
        user_id = session.get("user_id")
        g.user = None
        if user_id:
            user = User.find_one({ "_id": user_id })
            if user:
                g.user = user
        if g.user is None and self.require_auth:
            return json_response({ "errors": [ "You must authenticate first" ] }, 403)