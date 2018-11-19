from app.controllers.auth_controller import AuthController
from library.engine.utils import resolve_id, json_response, paginated_data, \
    get_request_fields, json_body_required, filter_query
from library.engine.permutation import expand_pattern_with_vars, apply_vars
from library.engine.errors import Conflict, HostNotFound, GroupNotFound, DatacenterNotFound, \
    Forbidden, ApiError, NotFound, NetworkGroupNotFound
from library.engine.action_log import logged_action
from flask import request
from copy import copy
from collections import defaultdict

hosts_ctrl = AuthController('hosts', __name__, require_auth=True)


@hosts_ctrl.route("/", methods=["GET"])
@hosts_ctrl.route("/<host_id>", methods=["GET"])
def show(host_id=None):
    from app.models import Host
    if host_id is None:
        query = {}
        if "_filter" in request.values:
            name_filter = request.values["_filter"]
            if len(name_filter) > 0:
                query["fqdn"] = filter_query(name_filter)
        if "group_id" in request.values:
            group_id = resolve_id(request.values["group_id"])
            query["group_id"] = group_id
        if "network_group_id" in request.values:
            sg_id = resolve_id(request.values["network_group_id"])
            query["network_group_id"] = sg_id
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
@json_body_required
def create():
    from app.models import Host, Group, Datacenter, NetworkGroup
    host_attrs = dict([x for x in request.json.items() if x[0] in Host.FIELDS])
    aliases_map = defaultdict(list)
    if "fqdn_pattern" in request.json:
        if "fqdn" in host_attrs:
            raise Conflict("fqdn field is not allowed due to fqdn_pattern param presence")
        hosts_data = list(expand_pattern_with_vars(request.json["fqdn_pattern"]))
        hostnames = []
        if "aliases" in host_attrs:
            for hostname, vars in hosts_data:
                hostnames.append(hostname)
                for alias in host_attrs["aliases"]:
                    aliases_map[hostname].append(apply_vars(alias, vars))
    else:
        hostnames = [host_attrs["fqdn"]]
        if "aliases" in host_attrs:
            aliases_map[host_attrs["fqdn"]] = host_attrs["aliases"]

        del(host_attrs["fqdn"])

    if "group_id" in host_attrs and host_attrs["group_id"] is not None:
        group = Group.get(host_attrs["group_id"], GroupNotFound("group not found"))
        if not group.modification_allowed:
            raise Forbidden("you don't have permissions to create hosts in this group")
        host_attrs["group_id"] = group._id

    if "network_group_id" in host_attrs and host_attrs["network_group_id"] is not None:
        sg = NetworkGroup.get(host_attrs["network_group_id"], NetworkGroupNotFound("server group not found"))
        if not sg.assigning_allowed:
            raise Forbidden("you don't have permissions to assign the given server group")
        host_attrs["network_group_id"] = sg._id

    if "datacenter_id" in host_attrs and host_attrs["datacenter_id"] is not None:
        datacenter = Datacenter.get(host_attrs["datacenter_id"], DatacenterNotFound("datacenter not found"))
        host_attrs["datacenter_id"] = datacenter._id

    for fqdn in hostnames:
        attrs = copy(host_attrs)
        attrs["fqdn"] = fqdn
        attrs["aliases"] = aliases_map[fqdn]
        host = Host(**attrs)
        host.save()

    hosts = Host.find({"fqdn": {"$in": list(hostnames) }})
    data = paginated_data(hosts.sort("fqdn"))
    return json_response(data, 201)


@hosts_ctrl.route("/<host_id>", methods=["PUT"])
@logged_action("host_update")
@json_body_required
def update(host_id):
    from app.models import Host, Group, Datacenter, NetworkGroup
    host = Host.get(host_id, HostNotFound("host not found"))
    host_attrs = dict([x for x in request.json.items() if x[0] in Host.FIELDS])

    if not host.modification_allowed:
        if host.system_modification_allowed:
            # if user is a system user, he still can update SYSTEM_FIELDS
            # so we cleanup everything but system fields in host_attrs
            host_attrs = dict([x for x in host_attrs.iteritems() if x[0] in Host.SYSTEM_FIELDS])
        else:
            # if user is not a system user he gets the heck out
            raise Forbidden("You don't have permissions to modify this host")

    if "group_id" in host_attrs and host_attrs["group_id"] is not None:
        group = Group.get(host_attrs["group_id"], GroupNotFound("group not found"))
        if not group.modification_allowed:
            raise Forbidden("You don't have permissions to move hosts to group %s" % group.name)
        host_attrs["group_id"] = group._id

    if "network_group_id" in host_attrs and host_attrs["network_group_id"] is not None:
        sg = NetworkGroup.get(host_attrs["network_group_id"], NetworkGroupNotFound("server group not found"))
        if not sg.assigning_allowed:
            raise Forbidden("you don't have permissions to assign the given server group")
        host_attrs["network_group_id"] = sg._id

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
@json_body_required
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
@json_body_required
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
@json_body_required
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
@json_body_required
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
        if not host.destruction_allowed:
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


@hosts_ctrl.route("/<host_id>/set_custom_fields", methods=["POST"])
@logged_action("host_set_custom_fields")
@json_body_required
def set_custom_fields(host_id):
    from app.models import Host
    host = Host.get(host_id, HostNotFound("host not found"))

    if not host.modification_allowed:
        raise Forbidden("You don't have permissions to modify this host")
    if not "custom_fields" in request.json:
        raise ApiError("no custom_fields provided")

    cfs = request.json["custom_fields"]
    if type(cfs) == dict:
        cfs = [{"key": x[0], "value": x[1]} for x in cfs.iteritems()]

    for item in cfs:
        host.set_custom_field(item["key"], item["value"])

    host.save()

    data = {"data": host.to_dict(get_request_fields())}
    return json_response(data)


@hosts_ctrl.route("/<host_id>/remove_custom_fields", methods=["POST", "DELETE"])
@logged_action("host_remove_custom_fields")
@json_body_required
def remove_custom_fields(host_id):
    from app.models import Host
    host = Host.get(host_id, HostNotFound("host not found"))

    if not host.modification_allowed:
        raise Forbidden("You don't have permissions to modify this host")
    if not "custom_fields" in request.json:
        raise ApiError("no custom_fields provided")

    cfs = request.json["custom_fields"]
    if type(cfs) == dict:
        cfs = [{"key": x} for x in cfs]

    for item in cfs:
        host.remove_custom_field(item["key"])

    host.save()

    data = {"data": host.to_dict(get_request_fields())}
    return json_response(data)


@hosts_ctrl.route("/<host_id>/add_tags", methods=["POST"])
@logged_action("host_add_tags")
@json_body_required
def add_tags(host_id):
    from app.models import Host
    host = Host.get(host_id, HostNotFound("host not found"))

    if not host.modification_allowed:
        raise Forbidden("You don't have permissions to modify this host")
    if not "tags" in request.json:
        raise ApiError("no tags provided")

    tags = request.json["tags"]
    if type(tags) != list:
        raise ApiError("tags should be an array type")

    for tag in tags:
        host.add_tag(tag)

    host.save()

    data = {"data": host.to_dict(get_request_fields())}
    return json_response(data)


@hosts_ctrl.route("/<host_id>/remove_tags", methods=["POST", "DELETE"])
@logged_action("host_remove_tags")
@json_body_required
def remove_tags(host_id):
    from app.models import Host
    host = Host.get(host_id, HostNotFound("host not found"))

    if not host.modification_allowed:
        raise Forbidden("You don't have permissions to modify this host")
    if not "tags" in request.json:
        raise ApiError("no tags provided")

    tags = request.json["tags"]
    if type(tags) != list:
        raise ApiError("tags should be an array type")

    for tag in tags:
        host.remove_tag(tag)

    host.save()

    data = {"data": host.to_dict(get_request_fields())}
    return json_response(data)
