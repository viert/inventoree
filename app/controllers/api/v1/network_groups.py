from library.engine.utils import resolve_id, paginated_data, json_response, \
    get_request_fields, json_body_required
from library.engine.permissions import get_user_from_app_context
from library.engine.errors import NetworkGroupNotFound, WorkGroupNotFound, IntegrityError, Forbidden, InputDataError
from app.controllers.auth_controller import AuthController
from library.engine.action_log import logged_action
from flask import request

network_groups_ctrl = AuthController('network_groups', __name__, require_auth=True)


@network_groups_ctrl.route("/", methods=["GET"])
@network_groups_ctrl.route("/<network_group_id>", methods=["GET"])
def show(network_group_id=None):
    from app.models import NetworkGroup
    if network_group_id is None:
        query = {}
        if "_filter" in request.values:
            name_filter = request.values["_filter"]
            if len(name_filter) > 0:
                query["name"] = { "$regex": "^%s" % name_filter }
        if "work_group_id" in request.values:
            work_group_id = resolve_id(request.values["work_group_id"])
            query["work_group_id"] = work_group_id
        elif "work_group_name" in request.values:
            from app.models import WorkGroup
            wg = WorkGroup.get(request.values["work_group_name"])
            if wg is None:
                query["work_group_id"] = None
            else:
                query["work_group_id"] = wg._id
        network_groups = NetworkGroup.find(query)
    else:
        network_group_id = resolve_id(network_group_id)
        network_groups = NetworkGroup.find({"$or": [
            { "_id": network_group_id },
            { "name": network_group_id }
        ]})
        if network_groups.count() == 0:
            raise NetworkGroupNotFound("server group not found")
    data = paginated_data(network_groups.sort("name"))
    return json_response(data)


@network_groups_ctrl.route("/", methods=["POST"])
@logged_action("network_group_create")
@json_body_required
def create():
    from app.models import NetworkGroup, WorkGroup

    user = get_user_from_app_context()
    if user is None or not user.system:
        raise Forbidden("only system users are allowed to create server groups")

    sgroup_attrs = request.json.copy()
    if "work_group_id" not in sgroup_attrs:
        if "work_group_name" in sgroup_attrs:
            work_group = WorkGroup.find_one({"name": sgroup_attrs["work_group_name"]})
            if work_group is not None:
                sgroup_attrs["work_group_id"] = work_group._id
                del(sgroup_attrs["work_group_name"])
            else:
                raise WorkGroupNotFound("work_group provided has not been found")
        else:
            raise IntegrityError("network_group has to be in a work_group")
    else:
        if sgroup_attrs["work_group_id"] is None:
            raise IntegrityError("group has to be in a work_group")
        work_group = WorkGroup.get(sgroup_attrs["work_group_id"], WorkGroupNotFound("work_group provided has not been found"))
        sgroup_attrs["work_group_id"] = work_group._id

    sgroup_attrs = dict([x for x in sgroup_attrs.items() if x[0] in NetworkGroup.FIELDS])
    network_group = NetworkGroup(**sgroup_attrs)
    network_group.save()
    return json_response({ "data": network_group.to_dict(get_request_fields()) }, 201)


@network_groups_ctrl.route("/<network_group_id>", methods=["DELETE"])
@logged_action("network_group_delete")
def destroy(network_group_id):
    from app.models import NetworkGroup
    user = get_user_from_app_context()
    if user is None or not user.system:
        raise Forbidden("only system users are allowed to create server groups")

    network_group_id = resolve_id(network_group_id)
    network_group = NetworkGroup.find_one({"$or": [
        { "_id": network_group_id },
        { "name": network_group_id }
    ]})

    if network_group is None:
        raise NetworkGroupNotFound("server group not found")

    network_group.clear_hosts()
    network_group.destroy()
    return json_response({ "data": network_group.to_dict(get_request_fields()) })
