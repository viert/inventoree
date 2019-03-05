from flask import request, make_response
from datetime import datetime
from app.controllers.auth_controller import AuthController
from library.engine.utils import json_response, cursor_to_list, get_app_version, get_boolean_request_param
from library.engine.errors import ApiError, WorkGroupNotFound

open_ctrl = AuthController("open", __name__, require_auth=False)


def get_executer_data(query, recursive=False, include_unattached=False):
    from app.models import WorkGroup, Datacenter, Group, Host

    host_fields = list(Host.FIELDS)
    group_fields = list(Group.FIELDS)

    if recursive:
        host_fields += ["all_tags", "all_custom_fields"]
        group_fields += ["all_tags", "all_custom_fields"]

    work_groups = WorkGroup.find(query)
    work_groups = cursor_to_list(work_groups)
    work_group_ids = [x["_id"] for x in work_groups]

    groups = Group.find({ "work_group_id": { "$in": work_group_ids }})
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
        "work_groups": work_groups,
        "groups": groups,
        "hosts": hosts
    }


@open_ctrl.route("/executer_data")
def executer_data():
    query = {}
    if "work_groups" in request.values:
        work_group_names = [x for x in request.values["work_groups"].split(",") if x != ""]
        if len(work_group_names) > 0:
            query["name"] = {"$in": work_group_names}

    recursive = get_boolean_request_param("recursive")
    include_unattached = get_boolean_request_param("include_unattached")

    results = get_executer_data(query, recursive, include_unattached)
    return json_response({"data": results})


@open_ctrl.route("/ansible")
def ansible():
    from app.models import WorkGroup
    from library.engine.utils import full_group_structure, ansible_group_structure

    if "work_groups" not in request.values:
        raise ApiError("work_groups query param is mandatory")

    work_group_names = [x for x in request.values["work_groups"].split(",") if x != ""]
    query = {"name": {"$in": work_group_names}}
    work_group_ids = [x._id for x in WorkGroup.find(query)]
    if not work_group_ids:
        raise WorkGroupNotFound("can't find any workgroup on your request")

    include_vars = get_boolean_request_param("vars")
    if include_vars:
        host_fields = ["fqdn", "group_id", "ansible_vars"]
    else:
        host_fields = ["fqdn", "group_id"]

    fmt = request.values.get("format", "plain")
    if fmt == "plain":
        structure = full_group_structure(work_group_ids, host_fields=host_fields)
        render = "# This ansible inventory file was rendered from inventoree database, %s\n# For more info on inventoree please refer to https://github.com/viert/inventoree\n\n" % datetime.now().isoformat()
        for group_id, group in structure.items():
            if len(group["all_hosts"]) > 0:
                render += "[%s]\n" % group["name"]
                if include_vars:
                    hosts = group["all_hosts"].values()
                    hosts.sort(key=lambda x: x["fqdn"])
                    for host in hosts:
                        render += host["fqdn"]
                        if host["ansible_vars"] is not None:
                            for key, value in host["ansible_vars"].iteritems():
                                render += " %s=%s" % (key, value)
                        render += "\n"
                else:
                    host_names = [x["fqdn"] for x in group["all_hosts"].values()]
                    host_names.sort()
                    for fqdn in host_names:
                        render += fqdn + "\n"
                    render += "\n\n"

        response = make_response(render)
        response.headers["Content-Type"] = "text/plain"
        return response
    elif fmt == "json":
        return json_response(ansible_group_structure(work_group_ids, include_vars))
    else:
        raise ApiError("Invalid format. Valid formats are either \"plain\" or \"json\". (Defaults to \"plain\"")


@open_ctrl.route("/app", methods=["GET", "POST"])
def info():
    from app import app

    results = {
        "app": {
            "name": "inventoree"
        }
    }

    results["app"]["version"] = get_app_version()
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

    return json_response({ "app_info": results })


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
