from app.controllers.auth_controller import AuthController
from library.engine.utils import resolve_id, json_response, paginated_data, \
    get_request_fields, json_body_required, filter_query, get_boolean_request_param
from library.engine.permissions import current_user_is_system, can_create_hosts
from library.engine.permutation import expand_pattern_with_vars, apply_vars
from library.engine.errors import Conflict, HostNotFound, GroupNotFound, DatacenterNotFound, \
    Forbidden, ApiError, NotFound, NetworkGroupNotFound
from library.engine.action_log import logged_action
from flask import request, g
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
        if get_boolean_request_param("_mine"):
            query["responsibles_usernames_cache"] = g.user.username

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


@hosts_ctrl.route("/<host_id>/custom_data/<key>", methods=["GET"])
def get_custom_data(host_id, key):
    from app.models import Host
    host_id = resolve_id(host_id)
    host = Host.get(host_id, HostNotFound('host not found'))
    return json_response({
        "key": key,
        "data": host.get_custom_data_by_key(key)
    })


@hosts_ctrl.route("/", methods=["POST"])
@logged_action("host_create")
@json_body_required
def create():
    if not can_create_hosts():
        raise Forbidden("you don't have permissions to create hosts")

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
        raise Forbidden("you don't have permissions to modify this host")

    if current_user_is_system():
        for field in host_attrs:
            if field not in Host.SYSTEM_FIELDS:
                raise Forbidden("system users can update only system fields")
    else:
        for field in host_attrs:
            if field in Host.SYSTEM_FIELDS:
                raise Forbidden("only system users can update system fields")

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
    data = {"data": host.to_dict(get_request_fields())}
    return json_response(data)


@hosts_ctrl.route("/discover", methods=["POST"])
@logged_action("host_discover")
@json_body_required
def discover():
    """
    Creates or updates host with a given fqdn, tags, custom_fields and system fields.
    Must be used by automation scripts and CMSes.
    """
    from app import app
    from app.models import Host, Group, WorkGroup

    if not current_user_is_system():
        raise Forbidden("discover handler is accessible only by system users")

    tags = []
    if "tags" in request.json:
        tags = request.json["tags"]
        if type(tags) != list:
            raise ApiError("tags must be an array")

    custom_fields = []
    if "custom_fields" in request.json:
        custom_fields = request.json["custom_fields"]
        if type(custom_fields) != list:
            raise ApiError("custom_fields must be an array")

    if "fqdn" not in request.json:
        raise ApiError("fqdn field is missing")
    fqdn = request.json["fqdn"]

    attrs = {}
    has_attrs = False
    for k, v in request.json.iteritems():
        if k not in Host.SYSTEM_FIELDS:
            continue
        attrs[k] = v
        has_attrs = True

    h = Host.find_one({"fqdn": fqdn})
    status_code = 200

    if h is None:
        # check for workgroup settings
        if "workgroup_name" in request.json:
            wg = WorkGroup.get(request.json["workgroup_name"], NotFound("Workgroup %s not found" % request.json["workgroup_name"]))
            if not wg.modification_allowed:
                raise Forbidden("this system user doesn't have permissions to modify or create a host in this workgroup"
                                " (consider including the user into workgroup or granting supervisor privileges)")
            default_group_postfix = app.config.app.get("DEFAULT_GROUP_POSTFIX", "_unknown")
            group_name = wg.name + default_group_postfix
            group = Group.get(group_name)
            if group is None:
                group = Group(name=group_name, work_group_id=wg._id, description="default group in %s workgroup" % wg.name)
                group.save()
            attrs["group_id"] = group._id
        attrs["fqdn"] = fqdn
        attrs["tags"] = tags
        attrs["custom_fields"] = custom_fields
        h = Host(**attrs)
        h.save()
        status_code = 201
    else:
        if has_attrs or len(tags) + len(custom_fields) > 0:
            for tag in tags:
                h.add_tag(tag)
            for cf in custom_fields:
                h.set_custom_field(cf["key"], cf["value"])
            h.update(attrs)

    data = {"data": h.to_dict(get_request_fields())}
    return json_response(data, status_code)


@hosts_ctrl.route("/<host_id>", methods=["DELETE"])
@logged_action("host_delete")
def delete(host_id):
    from app.models import Host
    host = Host.get(host_id, HostNotFound("host not found"))

    if not host.destruction_allowed:
        raise Forbidden("You don't have permission to delete this host")

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

@hosts_ctrl.route("/<host_id>/add_custom_data", methods=["POST"])
@logged_action("host_add_custom_data")
@json_body_required
def add_custom_data(host_id):
    from app.models import Host
    host = Host.get(host_id, HostNotFound("host not found"))

    if not host.modification_allowed:
        raise Forbidden("You don't have permissions to modify this host")
    if "custom_data" not in request.json:
        raise ApiError("no custom_data provided")

    cd = request.json["custom_data"]
    if type(cd) != dict:
        raise ApiError("custom_data must be a dict")

    host.add_local_custom_data(cd)
    host.save()

    data = {"data": host.to_dict(get_request_fields())}
    return json_response(data)


@hosts_ctrl.route("/<host_id>/remove_custom_data", methods=["POST", "DELETE"])
@logged_action("host_remove_custom_data")
@json_body_required
def remove_custom_data(host_id):
    from app.models import Host
    host = Host.get(host_id, HostNotFound("host not found"))

    if not host.modification_allowed:
        raise Forbidden("You don't have permissions to modify this host")
    if "keys" not in request.json:
        raise ApiError("no custom data keys provided")

    keys = request.json["keys"]
    if type(keys) == str or type(keys) == unicode:
        keys = [keys]
    elif type(keys) != list:
        raise ApiError("keys field must be a list or a string type")

    for key in keys:
        host.remove_local_custom_data(key)
    host.save()

    data = {"data": host.to_dict(get_request_fields())}
    return json_response(data)
