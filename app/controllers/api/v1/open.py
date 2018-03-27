from flask import request, make_response
from datetime import datetime
from app.controllers.auth_controller import AuthController
from library.engine.utils import json_response, cursor_to_list

open_ctrl = AuthController("open", __name__, require_auth=False)


def get_executer_data(query, recursive=False, include_unattached=False):
    from app.models import Project, Datacenter, Group, Host

    host_fields = list(Host.FIELDS)
    group_fields = list(Group.FIELDS)

    if recursive:
        host_fields += ["all_tags", "all_custom_fields"]
        group_fields += ["all_tags", "all_custom_fields"]

    projects = Project.find(query)
    projects = cursor_to_list(projects)
    project_ids = [x["_id"] for x in projects]

    groups = Group.find({ "project_id": { "$in": project_ids }})
    groups = cursor_to_list(groups, fields=group_fields)
    group_ids = [x["_id"] for x in groups]

    if include_unattached:
        hosts = Host.find({})
    else:
        hosts = Host.find({ "group_id": { "$in": group_ids }})
    hosts = cursor_to_list(hosts, fields=host_fields)

    datacenters = Datacenter.find({})
    datacenters = cursor_to_list(datacenters)
    return {
        "datacenters": datacenters,
        "projects": projects,
        "groups": groups,
        "hosts": hosts
    }


@open_ctrl.route("/executer_data")
def executer_data():
    query = {}
    if "projects" in request.values:
        project_names = [x for x in request.values["projects"].split(",") if x != ""]
        if len(project_names) > 0:
            query["name"] = { "$in": project_names }

    recursive = False
    include_unattached = False
    if "recursive" in request.values:
        recursive = request.values["recursive"].lower()
        if recursive in ["1","yes","true"]:
            recursive = True
        else:
            recursive = False

    if "include_unattached" in request.values:
        include_unattached = request.values["include_unattached"].lower()
        if include_unattached in ["1", "yes", "true"]:
            include_unattached = True
        else:
            include_unattached = False

    results = get_executer_data(query, recursive, include_unattached)
    return json_response({ "data": results })


@open_ctrl.route("/ansible")
def ansible():
    query = {}
    if "projects" in request.values:
        project_names = [x for x in request.values["projects"].split(",") if x != ""]
        if len(project_names) > 0:
            query["name"] = { "$in": project_names }
    from app.models import Project
    from library.engine.utils import full_group_structure
    project_ids = [x._id for x in Project.find(query).all()]
    structure = full_group_structure(project_ids)
    render = "# This ansible inventory file was rendered from conductor database, %s\n# For more info on conductor please refer to https://github.com/viert/conductor\n\n" % datetime.now().isoformat()
    for group_id, group in structure.items():
        if len(group["all_hosts"]) > 0:
            render += "[%s]\n" % group["name"]
            host_names = [x["fqdn"] for x in group["all_hosts"].values()]
            host_names.sort()
            for fqdn in host_names:
                render += fqdn + "\n"
            render += "\n\n"

    response = make_response(render)
    response.headers["Content-Type"] = "text/plain"
    return response

@open_ctrl.route("/app")
def conductor():
    from app import app

    results = {
        "app": {
            "name": "conductor"
        }
    }
    if "VERSION" in dir(app):
        results["app"]["version"] = app.VERSION
    else:
        results["app"]["version"] = "unknown"

    results["app"]["action_logging_enabled"] = app.action_logging

    from library.db import db
    results["mongodb"] = db.conn.client.server_info()

    import flask
    results["flask_version"] = flask.__version__

    from library.engine.cache import check_cache
    results["cache"] = {
        "type": app.cache.__class__.__name__,
        "active": check_cache()
    }

    return json_response({ "conductor_info": results })

def _get_hosts(group_names=None, tags=None):
    from app.models import Group
    if group_names is None:
        tag_query = [{ "tags": x } for x in tags]
        groups = Group.find({ "$or": tag_query })
    else:
        groups = Group.find({"name": {"$in": group_names}})

    all_hosts = set()
    for group in groups:
        all_hosts = all_hosts.union(group.all_hosts.all())

    if tags is not None:
        hosts = []
        for host in all_hosts:
            for tag in tags:
                if tag in host.all_tags:
                    hosts.append(host)
    else:
        hosts = list(all_hosts)

    return hosts


@open_ctrl.route("/resolve_hosts")
def resolve():
    from app.models import Host
    if "groups" not in request.values and "tags" not in request.values:
        return json_response({ "errors": ["You must provide groups and/or tags to search with"] })

    if "groups" in request.values:
        group_names = request.values["groups"].split(",")
    else:
        group_names = None

    if "tags" in request.values:
        tags = request.values["tags"].split(",")
    else:
        tags = None

    if "fields" in request.values:
        fields = request.values["fields"].split(",")
    else:
        fields = list(Host.FIELDS) + ["all_tags"]

    hosts = _get_hosts(group_names, tags)
    return json_response({ "data": cursor_to_list(hosts,fields) })
