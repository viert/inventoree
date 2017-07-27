from app.controllers.auth_controller import AuthController
from library.engine.utils import resolve_id, json_response, paginated_data, json_exception
from library.engine.permutation import expand_pattern
from flask import request
from bson.objectid import ObjectId, InvalidId


hosts_ctrl = AuthController('hosts', __name__, require_auth=True)


def _get_host_by_id(host_id):
    from app.models import Host
    host_id = resolve_id(host_id)
    return Host.find_one({
        "$or": [
            { "_id": host_id },
            { "fqdn": host_id }
        ]
    })


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
        hosts = Host.find(query)
    else:
        host_id = resolve_id(host_id)
        hosts = Host.find({ "$or": [
            { "_id": host_id },
            { "fqdn": host_id },
            { "short_name": host_id }
        ]})
    data = paginated_data(hosts.sort("fqdn"))
    return json_response(data)


@hosts_ctrl.route("/", methods=["POST"])
def create():
    from app.models import Host
    hosts_attrs = dict([x for x in request.json.items() if x[0] in Host.FIELDS])

    if "fqdn_pattern" in request.json:
        if "fqdn" in hosts_attrs:
            return json_response({ "errors": ["fqdn field is not allowed due to fqdn_pattern param presence"] })
        try:
            hostnames = list(expand_pattern(request.json["fqdn_pattern"]))
        except Exception as e:
            return json_exception(e)
    else:
        hostnames = [hosts_attrs["fqdn"]]
        del(hosts_attrs["fqdn"])

    try:
        hosts_attrs["group_id"] = ObjectId(hosts_attrs["group_id"])
    except (KeyError, InvalidId):
        hosts_attrs["group_id"] = None

    try:
        hosts_attrs["datacenter_id"] = ObjectId(hosts_attrs["datacenter_id"])
    except (KeyError, InvalidId):
        hosts_attrs["datacenter_id"] = None

    for fqdn in hostnames:
        attrs = hosts_attrs
        attrs["fqdn"] = fqdn
        host = Host(**attrs)
        try:
            host.save()
        except Exception as e:
            return json_exception(e, 500)

    hosts = Host.find({"fqdn": {"$in": list(hostnames) }})
    data = paginated_data(hosts.sort("fqdn"))
    return json_response(data)

@hosts_ctrl.route("/<host_id>", methods=["PUT"])
def update(host_id):
    host = _get_host_by_id(host_id)
    if host is None:
        return json_response({ "errors": [ "Host not found" ] }, 404)

    if not host.modification_allowed:
        return json_response({ "errors": [ "You don't have permissions to modify this host" ] }, 403)

    from app.models import Host
    hosts_attrs = dict([x for x in request.json.items() if x[0] in Host.FIELDS])

    try:
        hosts_attrs["group_id"] = ObjectId(hosts_attrs["group_id"])
    except InvalidId:
        hosts_attrs["group_id"] = None
    try:
        hosts_attrs["datacenter_id"] = ObjectId(hosts_attrs["datacenter_id"])
    except InvalidId:
        hosts_attrs["datacenter_id"] = None

    try:
        host.update(hosts_attrs)
    except Exception as e:
        return json_exception(e, 500)
    if "_fields" in request.values:
        fields = request.values["_fields"].split(",")
    else:
        fields = None
    return json_response({ "data": host.to_dict(fields) })


@hosts_ctrl.route("/<host_id>", methods=["DELETE"])
def delete(host_id):
    host = _get_host_by_id(host_id)

    if host is None:
        return json_response({ "errors": [ "Host not found" ] }, 404)

    if not host.destruction_allowed:
        return json_response({ "errors": [ "You don't have permissions to delete this host" ] }, 403)

    try:
        host.destroy()
    except Exception as e:
        return json_exception(e, 500)
    return json_response({ "data": host.to_dict() })
