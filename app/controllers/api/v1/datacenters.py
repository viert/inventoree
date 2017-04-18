from app.controllers.auth_controller import AuthController
from library.engine.utils import resolve_id, json_response, paginated_data


datacenters_ctrl = AuthController("datacenters", __name__, require_auth=True)


@datacenters_ctrl.route("/", methods=["GET"])
@datacenters_ctrl.route("/<datacenter_id>", methods=["GET"])
def show(datacenter_id=None):
    from app.models import Datacenter
    if datacenter_id is None:
        datacenters = Datacenter.find()
    else:
        datacenter_id = resolve_id(datacenter_id)
        datacenters = Datacenter.find({ "$or": {
            "_id": datacenter_id,
            "name": datacenter_id
        }})
    data = paginated_data(datacenters.sort("name"))
    for item in data["data"]:
        if "parent_id" not in item:
            item["parent_id"] = None
    return json_response(data)
