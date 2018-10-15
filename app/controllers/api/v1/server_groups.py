from library.engine.utils import resolve_id, paginated_data, json_response, \
    get_request_fields, get_user_from_app_context
from library.engine.errors import ServerGroupNotFound, WorkGroupNotFound, IntegrityError, Forbidden
from app.controllers.auth_controller import AuthController
from library.engine.action_log import logged_action
from flask import request

server_groups_ctrl = AuthController('server_groups', __name__, require_auth=True)


@server_groups_ctrl.route("/", methods=["GET"])
@server_groups_ctrl.route("/<server_group_id>", methods=["GET"])
def show(server_group_id=None):
    from app.models import ServerGroup
    if server_group_id is None:
        query = {}
        if "_filter" in request.values:
            name_filter = request.values["_filter"]
            if len(name_filter) >= 0:
                query["fqdn"] = { "$regex": "^%s" % name_filter }
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
        server_groups = ServerGroup.find(query)
    else:
        server_group_id = resolve_id(server_group_id)
        server_groups = ServerGroup.find({ "$or": [
            { "_id": server_group_id },
            { "name": server_group_id }
        ]})
        if server_groups.count() == 0:
            raise ServerGroupNotFound("server group not found")
    data = paginated_data(server_groups.sort("name"))
    return json_response(data)


@server_groups_ctrl.route("/", methods=["POST"])
@logged_action("server_group_create")
def create():
    from app.models import ServerGroup, WorkGroup

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
            raise IntegrityError("server_group has to be in a work_group")
    else:
        if sgroup_attrs["work_group_id"] is None:
            raise IntegrityError("group has to be in a work_group")
        work_group = WorkGroup.get(sgroup_attrs["work_group_id"], WorkGroupNotFound("work_group provided has not been found"))
        sgroup_attrs["work_group_id"] = work_group._id

    sgroup_attrs = dict([x for x in sgroup_attrs.items() if x[0] in ServerGroup.FIELDS])
    server_group = ServerGroup(**sgroup_attrs)
    server_group.save()
    return json_response({ "data": server_group.to_dict(get_request_fields()) }, 201)


@server_groups_ctrl.route("/<server_group_id>", methods=["DELETE"])
def destroy(server_group_id):
    from app.models import ServerGroup
    user = get_user_from_app_context()
    if user is None or not user.system:
        raise Forbidden("only system users are allowed to create server groups")

    server_group_id = resolve_id(server_group_id)
    server_group = ServerGroup.find_one({ "$or": [
        { "_id": server_group_id },
        { "name": server_group_id }
    ]})

    if server_group is None:
        raise ServerGroupNotFound("server group not found")

    server_group.clear_hosts()
    server_group.destroy()
    return json_response({ "data": server_group.to_dict(get_request_fields()) })
