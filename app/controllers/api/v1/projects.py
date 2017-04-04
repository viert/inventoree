from flask import Blueprint

projects_ctrl = Blueprint("projects", __name__)

@projects_ctrl.route("/")
def index():
    return "projects"