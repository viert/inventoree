from flask import Blueprint

albums_ctrl = Blueprint('albums', __name__)

@albums_ctrl.route("/")
def index():
    return "albums list"