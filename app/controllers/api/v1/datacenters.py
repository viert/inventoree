from app.controllers.auth_controller import AuthController
from library.engine.utils import resolve_id, json_response, paginated_data, json_exception
from flask import request
from bson.objectid import ObjectId


datacenters_ctrl = AuthController("datacenters", __name__, require_auth=True)


def _get_dc_by_id(dc_id):
    from app.models import Datacenter
    dc_id = resolve_id(dc_id)
    return Datacenter.find_one({
        "$or": [
            { "_id": dc_id },
            { "name": dc_id }
        ]
    })


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
        ]})
    data = paginated_data(datacenters.sort("name"))
    return json_response(data)

@datacenters_ctrl.route("/", methods=["POST"])
def create():
    from app.models import Datacenter
    dc_attrs = dict([x for x in request.json.items() if x[0] in Datacenter.FIELDS])
    dc = Datacenter(**dc_attrs)
    # TODO: check permissions!
    try:
        dc.save()
    except Exception as e:
        return json_exception(e, 500)
    if "parent_id" in dc_attrs and dc_attrs["parent_id"]:
        return set_parent(dc._id)
    return json_response({ "data": dc.to_dict() }, 201)

@datacenters_ctrl.route("/<dc_id>", methods=["PUT"])
def update(dc_id):
    dc = _get_dc_by_id(dc_id)
    if dc is None:
        return json_response({ "errors": ["Datacenter not found"] }, 404)
    # TODO: check permissions!
    try:
        dc.update(request.json)
    except Exception as e:
        return json_exception(e, 500)
    if "parent_id" in request.json:
        parent_id = resolve_id(request.json["parent_id"])
        if parent_id != dc.parent_id:
            return set_parent(dc._id)
    return json_response({ "data": dc.to_dict() })

@datacenters_ctrl.route("/<dc_id>", methods=["DELETE"])
def delete(dc_id):
    dc = _get_dc_by_id(dc_id)
    if dc is None:
        return json_response({ "errors": ["Datacenter not found"] }, 404)
    # TODO: check permissions!
    try:
        dc.destroy()
    except Exception as e:
        return json_exception(e, 500)
    return json_response({ "data": dc.to_dict() })

@datacenters_ctrl.route("/<dc_id>/set_parent", methods=["PUT"])
def set_parent(dc_id):
    dc = _get_dc_by_id(dc_id)
    if dc is None:
        return json_response({ "errors": ["Datacenter not found"] }, 404)
    # TODO: check permissions!
    parent_id = request.json.get("parent_id")
    if dc.parent:
        try:
            dc.unset_parent()
        except Exception as e:
            return json_exception(e, 500)
    if parent_id is not None:
        try:
            parent_id = resolve_id(parent_id)
            dc.set_parent(parent_id)
        except Exception as e:
            return json_exception(e, 500)
    return json_response({ "data": dc.to_dict() })