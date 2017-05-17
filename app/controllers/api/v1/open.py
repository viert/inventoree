from flask import request
from bson.objectid import ObjectId, InvalidId
from app.controllers.auth_controller import AuthController
from library.engine.utils import resolve_id, json_response, json_exception, cursor_to_list, diff

open_ctrl = AuthController("open", __name__, require_auth=False)


@open_ctrl.route("/projects2groups/<project_id>")
def projects2groups(project_id):
    from app.models import Project
    project_id = resolve_id(project_id)

    fields = request.values.get("fields")
    if fields is None:
        fields = ["name"]
    else:
        fields = fields.split(',')


    project = Project.find_one({"$or": [
        { "_id": project_id },
        { "name": project_id }
    ]})
    if project is None:
        return json_response({ 'errors': [ "No project found" ]}, 404)
    groups = cursor_to_list(project.groups, fields=fields)
    return json_response(groups)

@open_ctrl.route("/groups/<group_id>")
def groups(group_id):
    from app.models import Group
    group_id = resolve_id(group_id)

    fields = request.values.get("fields")
    if fields is None:
        fields = [ "_id", "name", "description", "project_name", "created_at", "updated_at", "parents", "children" ]
    else:
        fields = fields.split(',')

    groups = Group.find({ "$or": [
        { "_id": group_id },
        { "name": group_id }
    ]})

    groups = cursor_to_list(groups, fields=fields)
    for group in groups:
        group["parents"] = [x.name for x in group["parents"]]
        group["children"] = [x.name for x in group["children"]]
    return json_response(groups)

@open_ctrl.route("/groups2hosts/<group_id>")
def groups2hosts(group_id):
    from app.models import Group
    group_id = resolve_id(group_id)

    fields = request.values.get("fields")
    if fields is None:
        fields = ["fqdn"]
    else:
        fields = fields.split(',')
    
    group = Group.find_one({ "$or": [
        { "_id": group_id },
        { "name": group_id }
    ]})

    if group is None:
        return json_response({ 'errors': [ "No group found" ]}, 404)

    hosts = cursor_to_list(group.hosts, fields=fields)
    return json_response(hosts)

@open_ctrl.route("/datacenters.json")
def datacenters():
    from app.models import Datacenter

    dcs = Datacenter.find({})
    dcs = cursor_to_list(dcs, fields=["name", "parent", "children", "human_readable"])
    for dc in dcs:
        if dc["parent"] is not None:
            dc["parent"] = dc["parent"].name
        dc["children"] = [x.name for x in dc["children"]]
    return json_response(dcs)