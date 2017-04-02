from flask import Blueprint

main_ctrl = Blueprint("main", __name__)

@main_ctrl.route("/")
def index():
    return "Hello world"