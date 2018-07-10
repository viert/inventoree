from app.controllers.auth_controller import AuthController
from library.engine.utils import resolve_id, json_response, paginated_data, get_request_fields
from library.engine.permutation import expand_pattern
from library.engine.errors import Conflict, HostNotFound, GroupNotFound, DatacenterNotFound, \
    Forbidden, ApiError, NotFound
from library.engine.action_log import logged_action
from flask import request
from copy import copy

hosts_ctrl = AuthController('hosts', __name__, require_auth=True)


@hosts_ctrl.route("/", methods=["GET"])
@hosts_ctrl.route("/<host_id>", methods=["GET"])
def show(host_id=None):
    from app.models import Host
    if host_id is None:
        query = {}
        if "_filter" in request.values:
            name_filter = request.values["_filter"]
            if len(name_filter) >= 2:
                query["fqdn"] = { "$regex": "^%s" % name_filter }
        if "group_id" in request.values:
            group_id = resolve_id(request.values["group_id"])
            query["group_id"] = group_id
        if "tags" in request.values:
            tags = request.values["tags"].split(",")
            query["tags"] = {"$in": tags}
        elif "all_tags" in request.values:
            tags = request.values["all_tags"].split(",")
            from app.models import Group
            groups = Group.find_by_tags_recursive(tags)
            group_ids = [x._id for x in groups]
            query["$or"] = [
                {"tags": {"$in": tags}},
                {"group_id": {"$in": group_ids}}
            ]
        hosts = Host.find(query)
    else:
        host_id = resolve_id(host_id)
        hosts = Host.find({ "$or": [
            { "_id": host_id },
            { "fqdn": host_id }
        ]})
        if hosts.count() == 0:
            hosts = Host.find({"aliases": host_id})
            if hosts.count() == 0:
                raise HostNotFound("host not found")
    data = paginated_data(hosts.sort("fqdn"))
    return json_response(data)


@hosts_ctrl.route("/", methods=["POST"])
@logged_action("host_create")
def create():
    from app.models import Host, Group, Datacenter
    host_attrs = dict([x for x in request.json.items() if x[0] in Host.FIELDS])
    if "fqdn_pattern" in request.json:
        if "fqdn" in host_attrs:
            raise Conflict("fqdn field is not allowed due to fqdn_pattern param presence")
        hostnames = list(expand_pattern(request.json["fqdn_pattern"]))
    else:
        hostnames = [host_attrs["fqdn"]]
        del(host_attrs["fqdn"])

    if "group_id" in host_attrs and host_attrs["group_id"] is not None:
        group = Group.get(host_attrs["group_id"], GroupNotFound("group not found"))
        host_attrs["group_id"] = group._id

    if "datacenter_id" in host_attrs and host_attrs["datacenter_id"] is not None:
        datacenter = Datacenter.get(host_attrs["datacenter_id"], DatacenterNotFound("datacenter not found"))
        host_attrs["datacenter_id"] = datacenter._id

    for fqdn in hostnames:
        attrs = copy(host_attrs)
        attrs["fqdn"] = fqdn
        host = Host(**attrs)
        host.save()

    hosts = Host.find({"fqdn": {"$in": list(hostnames) }})
    data = paginated_data(hosts.sort("fqdn"))
    return json_response(data, 201)


@hosts_ctrl.route("/<host_id>", methods=["PUT"])
@logged_action("host_update")
def update(host_id):
    from app.models import Host, Group, Datacenter
    host = Host.get(host_id, HostNotFound("host not found"))

    if not host.modification_allowed:
        raise Forbidden("You don't have permissions to modify this host")

    host_attrs = dict([x for x in request.json.items() if x[0] in Host.FIELDS])

    if "group_id" in host_attrs and host_attrs["group_id"] is not None:
        group = Group.get(host_attrs["group_id"], GroupNotFound("group not found"))
        host_attrs["group_id"] = group._id

    if "datacenter_id" in host_attrs and host_attrs["datacenter_id"] is not None:
        datacenter = Datacenter.get(host_attrs["datacenter_id"], DatacenterNotFound("datacenter not found"))
        host_attrs["datacenter_id"] = datacenter._id

    host.update(host_attrs)
    data = { "data": host.to_dict(get_request_fields()) }
    return json_response(data)


@hosts_ctrl.route("/<host_id>", methods=["DELETE"])
@logged_action("host_delete")
def delete(host_id):
    from app.models import Host
    host = Host.get(host_id, HostNotFound("host not found"))

    if not host.destruction_allowed:
        raise Forbidden("You don't have permission to modify this host")

    host.destroy()
    return json_response({ "data": host.to_dict(get_request_fields()) })


@hosts_ctrl.route("/mass_move", methods=["POST"])
@logged_action("host_mass_move")
def mass_move():
    if "host_ids" not in request.json or request.json["host_ids"] is None:
        raise ApiError("no host_ids provided")
    if type(request.json["host_ids"]) != list:
        raise ApiError("host_ids must be an array type")

    from app.models import Host, Group

    # resolving group
    group = Group.get(request.json["group_id"], GroupNotFound("group not found"))

    # resolving hosts
    host_ids = [resolve_id(x) for x in request.json["host_ids"]]
    host_ids = set([x for x in host_ids if x is not None])
    hosts = Host.find({"_id":{"$in": list(host_ids)}})
    hosts = [h for h in hosts if h.group_id != group._id]
    if len(hosts) == 0:
        raise NotFound("no hosts found to be moved")

    if not group.modification_allowed:
        raise Forbidden("you don't have permission to move hosts to group %s" % group.name)

    failed_hosts = []
    for host in hosts:
        if not host.modification_allowed:
            failed_hosts.append(host)
    if len(failed_hosts) > 0:
        failed_hosts = ', '.join([h.fqdn for h in failed_hosts])
        raise Forbidden("you don't have permission to modify hosts: %s" % failed_hosts)

    # moving hosts
    for host in hosts:
        host.group_id = group._id
        host.save()

    result = {
        "status": "ok",
        "data": {
            "group": group.to_dict(),
            "hosts": [host.to_dict() for host in hosts]
        }
    }

    return json_response(result)


@hosts_ctrl.route("/mass_set_datacenter", methods=["POST"])
@logged_action("host_mass_set_datacenter")
def mass_set_datacenter():
    if "host_ids" not in request.json or request.json["host_ids"] is None:
        raise ApiError("no host_ids provided")
    if type(request.json["host_ids"]) != list:
        raise ApiError("host_ids must be an array type")

    from app.models import Host, Datacenter

    # resolving datacenter
    datacenter = Datacenter.get(request.json["datacenter_id"], DatacenterNotFound("datacenter not found"))

    # resolving hosts
    host_ids = [resolve_id(x) for x in request.json["host_ids"]]
    host_ids = set([x for x in host_ids if x is not None])
    hosts = Host.find({"_id":{"$in": list(host_ids)}})
    hosts = [h for h in hosts if h.datacenter_id != datacenter._id]
    if len(hosts) == 0:
        raise NotFound("no hosts found to be moved")

    failed_hosts = []
    for host in hosts:
        if not host.modification_allowed:
            failed_hosts.append(host)
    if len(failed_hosts) > 0:
        failed_hosts = ', '.join([h.fqdn for h in failed_hosts])
        raise Forbidden("you don't have permission to modify hosts: %s" % failed_hosts)

    # setting hosts' datacenter
    for host in hosts:
        host.datacenter_id = datacenter._id
        host.save()

    result = {
        "status": "ok",
        "data": {
            "datacenter": datacenter.to_dict(),
            "hosts": [host.to_dict() for host in hosts]
        }
    }
    return json_response(result)


@hosts_ctrl.route("/mass_detach", methods=["POST"])
@logged_action("host_mass_detach")
def mass_detach():
    if "host_ids" not in request.json or request.json["host_ids"] is None:
        raise ApiError("no host_ids provided")
    if type(request.json["host_ids"]) != list:
        raise ApiError("host_ids must be an array type")

    from app.models import Host

    # resolving hosts
    host_ids = [resolve_id(x) for x in request.json["host_ids"]]
    host_ids = set([x for x in host_ids if x is not None])
    hosts = Host.find({"_id":{"$in": list(host_ids)}}).all()
    if len(hosts) == 0:
        raise NotFound("no hosts found to be moved")

    failed_hosts = []
    for host in hosts:
        if not host.modification_allowed:
            failed_hosts.append(host)
    if len(failed_hosts) > 0:
        failed_hosts = ', '.join([h.fqdn for h in failed_hosts])
        raise Forbidden("you don't have permission to modify hosts: %s" % failed_hosts)

    # moving hosts
    for host in hosts:
        host.group_id = None
        host.save()

    result = {
        "status": "ok",
        "data": {
            "hosts": [host.to_dict() for host in hosts]
        }
    }

    return json_response(result)


@hosts_ctrl.route("/mass_delete", methods=["POST"])
@logged_action("host_mass_delete")
def mass_delete():
    if "host_ids" not in request.json or request.json["host_ids"] is None:
        raise ApiError("no host_ids provided")
    if type(request.json["host_ids"]) != list:
        raise ApiError("host_ids must be an array type")

    from app.models import Host

    # resolving hosts
    host_ids = [resolve_id(x) for x in request.json["host_ids"]]
    host_ids = set([x for x in host_ids if x is not None])
    hosts = Host.find({"_id":{"$in": list(host_ids)}}).all()
    if len(hosts) == 0:
        raise NotFound("no hosts found to be moved")

    failed_hosts = []
    for host in hosts:
        if not host.modification_allowed:
            failed_hosts.append(host)
    if len(failed_hosts) > 0:
        failed_hosts = ', '.join([h.fqdn for h in failed_hosts])
        raise Forbidden("you don't have permission to modify hosts: %s" % failed_hosts)

    for host in hosts:
        host.destroy()

    result = {
        "status": "ok",
        "data": {
            "hosts": [x.to_dict() for x in hosts]
        }
    }

    return json_response(result)
