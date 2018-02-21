from flask import g, request
from library.engine.errors import AuthenticationError

AUTHENTICATION_URL = None

class LocalAuthorizer(object):

    def __init__(self, flask_app=None):
        self.flask = flask_app

    @staticmethod
    def get_authentication_url():
        return AUTHENTICATION_URL

    @staticmethod
    def get_user_data():
        if g.user:
            user_data = g.user.to_dict()
            if "password_hash" in user_data:
                del (user_data["password_hash"])
            return user_data

        from app.models import User
        data = request.json
        if data is None:
            raise AuthenticationError("No JSON in POST data", 400)
        if "username" not in data or "password" not in data:
            raise AuthenticationError("Insufficient fields for authenticate handler", 400)

        user = User.find_one({ "username": data["username"] })
        if not user or not user.check_password(data["password"]):
            raise AuthenticationError("Invalid username or password")

        user_data = user.to_dict()
        if "password_hash" in user_data:
            del(user_data["password_hash"])
        return user_data