from flask import request
from app.controllers.auth_controller import AuthController
from library.engine.utils import json_response, cursor_to_list

open_ctrl = AuthController("open", __name__, require_auth=False)

@open_ctrl.route("/executer_data")
def executer_data():
    from app.models import Project, Datacenter, Group, Host
    if "projects" not in request.values:
        return json_response({ "errors": [ "'projects' parameter is required for executer_data handler"]}, 400)
    project_names = request.values["projects"].split(",")

    projects = Project.find({ "name": { "$in": project_names }})
    projects = cursor_to_list(projects)
    project_ids = [x["_id"] for x in projects]

    groups = Group.find({ "project_id": { "$in": project_ids }})
    groups = cursor_to_list(groups)
    group_ids = [x["_id"] for x in groups]

    hosts = Host.find({ "group_id": { "$in": group_ids }})
    hosts = cursor_to_list(hosts)

    datacenters = Datacenter.find({})
    datacenters = cursor_to_list(datacenters)

    results = {
        "datacenters": datacenters,
        "projects": projects,
        "groups": groups,
        "hosts": hosts
    }
    return json_response({ "data": results })
