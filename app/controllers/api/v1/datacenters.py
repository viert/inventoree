from app.controllers.auth_controller import AuthController
from library.engine.utils import resolve_id, json_response, paginated_data
from flask import request


datacenters_ctrl = AuthController("datacenters", __name__, require_auth=True)


@datacenters_ctrl.route("/", methods=["GET"])
@datacenters_ctrl.route("/<datacenter_id>", methods=["GET"])
def show(datacenter_id=None):
    from app.models import Datacenter
    if datacenter_id is None:
        query = {}
        if "_filter" in request.values:
            name_filter = request.values["_filter"]
            if len(name_filter) >= 2:
                query["name"] = { "$regex": "^%s" % name_filter }
        datacenters = Datacenter.find(query)
    else:
        datacenter_id = resolve_id(datacenter_id)
        datacenters = Datacenter.find({ "$or": [
            { "_id": datacenter_id },
            { "name": datacenter_id }
        ]
        })
    data = paginated_data(datacenters.sort("name"))
    for item in data["data"]:
        if "parent_id" not in item:
            item["parent_id"] = None
    return json_response(data)
