from app.controllers.auth_controller import AuthController
from library.engine.utils import resolve_id, json_response, paginated_data
from flask import request


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