from flask import request, session, redirect
import requests
import json

CLIENT_ID = 0
CLIENT_SECRET = ""
OAUTH_SCOPE = 0
REDIRECT_URI = "/oauth_callback"


class VkAuthorizer(object):

    def __init__(self, flask_app=None):
        self.flask = flask_app
        self.flask.add_url_rule("/oauth_callback", "oauth_callback", self.oauth_callback)

    def oauth_callback(self):
        code = request.args.get("code")
        access_data = requests.get("https://oauth.vk.com/access_token?client_id=%s&client_secret=%s&redirect_uri=%s&code=%s" % (
            CLIENT_ID,
            CLIENT_SECRET,
            self.get_redirect_url(),
            code
        ))
        json_data = json.loads(access_data.content)
        if "error" in json_data:
            from app import app
            app.logger.error("Error in VK Authentication: %s" % json_data["error_description"])
        else:
            access_token = json_data["access_token"]
            user_id = json_data["user_id"]
            user_data = self.get_user_data(access_token, user_id)
            from app.models import User
            user = User.find_one({"ext_id": user_id})
            if user is None:
                user = User(
                    first_name=user_data["first_name"],
                    last_name=user_data["last_name"],
                    username=user_data["screen_name"],
                    ext_id=user_data["id"]
                )
                user.save()
            session["user_id"] = user._id
        return redirect("http://localhost:3000")

    def get_redirect_url(self):
        return "http://%s%s" % ( request.headers.get("Host"), REDIRECT_URI )

    def get_authentication_url(self):
        auth_url = "https://oauth.vk.com/authorize?client_id=%s&scope=%s&redirect_uri=%s" % (
            CLIENT_ID,
            OAUTH_SCOPE,
            self.get_redirect_url()
        )
        return auth_url

    def get_user_data(self, access_token, user_id):
        user_data = requests.get("https://api.vk.com/method/users.get?user_ids=%s&access_token=%s&v=5.69&fields=screen_name" %
                                 ( user_id, access_token )
                    )
        user_data = json.loads(user_data.content)
        return user_data["response"][0]