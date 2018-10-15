from flask import request
from bson.objectid import ObjectId
from app.controllers.auth_controller import AuthController
from library.engine.errors import GroupNotFound, Forbidden, ApiError, WorkGroupNotFound, NotFound, IntegrityError
from library.engine.utils import resolve_id, json_response, paginated_data, diff, get_request_fields
from library.engine.action_log import logged_action

groups_ctrl = AuthController("groups", __name__, require_auth=True)


@groups_ctrl.route("/")
@groups_ctrl.route("/<group_id>")
def show(group_id=None):
    from app.models import Group
    if group_id is None:
        query = {}
        if "_filter" in request.values:
            name_filter = request.values["_filter"]
            if len(name_filter) >= 0:
                query["name"] = { "$regex": "^%s" % name_filter }
        if "work_group_id" in request.values:
            work_group_id = resolve_id(request.values["work_group_id"])
            query["work_group_id"] = work_group_id
        if "tags" in request.values:
            tags = request.values["tags"].split(",")
            query["tags"] = { "$in": tags }
        elif "all_tags" in request.values:
            tags = request.values["all_tags"].split(",")
            query = Group.query_by_tags_recursive(tags, query)
        groups = Group.find(query)
    else:
        group_id = resolve_id(group_id)
        groups = Group.find({"$or": [
            { "_id": group_id },
            { "name": group_id }
        ]})
        if groups.count() == 0:
            raise GroupNotFound("group not found")

    data = paginated_data(groups.sort("name"))
    return json_response(data)


@groups_ctrl.route("/<group_id>/structure")
def structure(group_id):
    from app.models import Group
    from library.engine.graph import group_structure
    group = Group.get(group_id, GroupNotFound("group not found"))
    fields = get_request_fields()
    if "_host_fields" in request.values:
        host_fields = request.values["_host_fields"].split(",")
    else:
        host_fields = None
    data = group_structure(group, fields, host_fields)
    return json_response({ "data": data })


@groups_ctrl.route("/<group_id>", methods=["PUT"])
@logged_action("group_update")
def update(group_id):
    from app.models import WorkGroup, Group
    group = Group.get(group_id, GroupNotFound("group not found"))
    if not group.modification_allowed:
        raise Forbidden("you don't have permission to modify this group")
    group_attrs = request.json.copy()
    if "work_group_id" in group_attrs and group_attrs["work_group_id"] is not None:
        work_group = WorkGroup.get(group_attrs["work_group_id"], WorkGroupNotFound("work_group provided has not been found"))
        group_attrs["work_group_id"] = work_group._id
    group.update(group_attrs)
    return json_response({ "data": group.to_dict(get_request_fields()) })


@groups_ctrl.route("/<group_id>/set_children", methods=["PUT"])
@logged_action("group_set_children")
def set_children(group_id):
    from app.models import Group
    group = Group.get(group_id, GroupNotFound("group not found"))
    if not group.modification_allowed:
        raise Forbidden("you don't have permission to modify this group")
    orig = group.child_ids
    upd = request.json["child_ids"]
    upd = [ObjectId(x) for x in upd if x is not None]
    d = diff(orig, upd)
    exs = []
    for item in d.remove:
        try:
            group.remove_child(item)
        except Exception as e:
            exs.append(e)
    for item in d.add:
        try:
            group.add_child(item)
        except Exception as e:
            exs.append(e)
    if len(exs) > 0:
        raise ApiError(["%s: %s" % (x.__class__.__name__, x.message) for x in exs])
    return json_response({ "data": group.to_dict(get_request_fields()), "status": "ok" })


@groups_ctrl.route("/<group_id>/set_hosts", methods=["PUT"])
@logged_action("group_set_hosts")
def set_hosts(group_id):
    from app.models import Host, Group
    group = Group.get(group_id, GroupNotFound("group not found"))
    if not group.modification_allowed:
        raise Forbidden("you don't have permission to modify this group")
    orig = group.host_ids
    upd = request.json["host_ids"]
    upd = [ObjectId(x) for x in upd if x is not None]
    d =  diff(orig, upd)
    exs = []
    for item in d.remove:
        try:
            h = Host.find_one({ "_id": item })
            if h is not None:
                h.group_id = None
                h.save()
        except Exception as e:
            exs.append(e)
    for item in d.add:
        try:
            h = Host.find_one({ "_id": item })
            if h is not None:
                h.group_id = group._id
                h.save()
        except Exception as e:
            exs.append(e)
    if len(exs) > 0:
        raise ApiError(["%s: %s" % (x.__class__.__name__, x.message) for x in exs])
    return json_response({ "data": group.to_dict(get_request_fields()), "status": "ok" })


@groups_ctrl.route("/", methods=["POST"])
@logged_action("group_create")
def create():
    from app.models import Group, WorkGroup
    group_attrs = request.json.copy()
    if "work_group_id" not in group_attrs:
        if "work_group_name" in group_attrs:
            work_group = WorkGroup.find_one({"name": group_attrs["work_group_name"]})
            if work_group is not None:
                group_attrs["work_group_id"] = work_group._id
                del(group_attrs["work_group_name"])
            else:
                raise WorkGroupNotFound("work_group provided has not been found")
        else:
            raise IntegrityError("group has to be in a work_group")
    else:
        if group_attrs["work_group_id"] is None:
            raise IntegrityError("group has to be in a work_group")
        work_group = WorkGroup.get(group_attrs["work_group_id"], WorkGroupNotFound("work_group provided has not been found"))
        group_attrs["work_group_id"] = work_group._id

    group_attrs = dict([x for x in group_attrs.items() if x[0] in Group.FIELDS])
    if not work_group.modification_allowed:
        raise Forbidden("you don't have permission to create groups in this work_group")
    group = Group(**group_attrs)
    group.save()
    return json_response({ "data": group.to_dict(get_request_fields()) }, 201)

@groups_ctrl.route("/<group_id>", methods=["DELETE"])
@logged_action("group_delete")
def delete(group_id):
    from app.models import Group
    group = Group.get(group_id, GroupNotFound("group not found"))
    if not group.modification_allowed:
        raise Forbidden("you don't have permission to modify this group")
    group.destroy()
    return json_response({ "data": group.to_dict(get_request_fields()) })


@groups_ctrl.route("/mass_move", methods=["POST"])
@logged_action("group_mass_move")
def mass_move():
    # every group requested will move to the indicated work_group with all its' children
    # group will be detached from all its' parents due to not being able to have
    # relations between different work_groups

    if "group_ids" not in request.json or request.json["group_ids"] is None:
        raise ApiError("no group ids provided")
    if type(request.json["group_ids"]) != list:
        raise ApiError("group_ids must be an array type")
    if "work_group_id" not in request.json:
        raise ApiError("no work_group_id provided")

    from app.models import Group, WorkGroup
    # resolving WorkGroup
    work_group = WorkGroup.get(request.json["work_group_id"], WorkGroupNotFound("work_group not found"))
    # resolving Groups and their children
    group_ids = [resolve_id(x) for x in request.json["group_ids"]]
    group_ids = set([x for x in group_ids if x is not None])
    groups = Group.find({ "_id": { "$in": list(group_ids) }})
    groups = [g for g in groups if g is not None and g.work_group_id != work_group._id] # don't affect groups already in the work_group

    if len(groups) == 0:
        raise NotFound("no groups found to be moved")

    disallowed = []
    for g in groups:
        if not g.modification_allowed:
            disallowed.append(g.name)
    if len(disallowed) > 0:
        raise Forbidden("You don't have permissions to modify groups [%s]" % ', '.join(disallowed))

    all_groups = set()
    for group in groups:
        all_groups.add(group)
        for child in group.get_all_children():
            all_groups.add(child)

    # detaching high level groups from parents
    # TODO: fix algorithm, if we move group and it's child to a new work_group
    # we don't have to detach children from it's parent, this is to be resolved
    # properly

    for group in groups:
        group.remove_all_parents()

    # moving all groups and their children to the new work_group
    for group in all_groups:
        group.work_group_id = work_group._id
        group.save(skip_callback=True)

    result = {
        "status": "ok",
        "data": {
            "work_group": work_group.to_dict(),
            "groups": [x.to_dict() for x in all_groups]
        }
    }

    return json_response(result)

@groups_ctrl.route("/mass_delete", methods=["POST"])
@logged_action("group_mass_delete")
def mass_delete():
    if "group_ids" not in request.json or request.json["group_ids"] is None:
        raise ApiError("no group ids provided")
    if type(request.json["group_ids"]) != list:
        raise ApiError("group_ids must be an array type")

    from app.models import Group

    # resolving Groups
    group_ids = [resolve_id(x) for x in request.json["group_ids"]]
    group_ids = set([x for x in group_ids if x is not None])
    query = {"_id": {"$in": list(group_ids)}}
    groups = Group.find(query)

    if groups.count() == 0:
        raise NotFound("no groups found to be deleted")

    groups = groups.all()

    disallowed = []
    for g in groups:
        if not g.modification_allowed:
            disallowed.append(g.name)
    if len(disallowed) > 0:
        raise Forbidden("You don't have permissions to delete groups [%s]" % ', '.join(disallowed))

    for group in groups:
        group.remove_all_children()
        group.remove_all_hosts()

    # reload
    groups = Group.find(query)

    for group in groups:
        group.destroy()

    result = {
        "status": "ok",
        "data": {
            "groups": [x.to_dict() for x in groups]
        }
    }
    return json_response(result)

@groups_ctrl.route("/<group_id>/set_custom_fields", methods=["POST"])
@logged_action("group_set_custom_fields")
def set_custom_fields(group_id):
    from app.models import Group
    group = Group.get(group_id, GroupNotFound("group not found"))

    if not group.modification_allowed:
        raise Forbidden("You don't have permissions to modify this group")

    if not "custom_fields" in request.json:
        raise ApiError("no custom_fields provided")

    cfs = request.json["custom_fields"]
    if type(cfs) == dict:
        cfs = [{"key": x[0], "value": x[1]} for x in cfs.iteritems()]

    for item in cfs:
        group.set_custom_field(item["key"], item["value"])

    group.save()

    data = {"data": group.to_dict(get_request_fields())}
    return json_response(data)


@groups_ctrl.route("/<group_id>/remove_custom_fields", methods=["POST", "DELETE"])
@logged_action("group_remove_custom_fields")
def remove_custom_fields(group_id):
    from app.models import Group
    group = Group.get(group_id, GroupNotFound("group not found"))

    if not group.modification_allowed:
        raise Forbidden("You don't have permissions to modify this group")

    if not "custom_fields" in request.json:
        raise ApiError("no custom_fields provided")

    cfs = request.json["custom_fields"]
    if type(cfs) == dict:
        cfs = [{"key": x} for x in cfs]

    for item in cfs:
        group.remove_custom_field(item["key"])

    group.save()

    data = {"data": group.to_dict(get_request_fields())}
    return json_response(data)


@groups_ctrl.route("/<group_id>/add_tags", methods=["POST"])
@logged_action("group_add_tags")
def add_tags(group_id):
    from app.models import Group
    group = Group.get(group_id, GroupNotFound("group not found"))

    if not group.modification_allowed:
        raise Forbidden("You don't have permissions to modify this group")

    if not "tags" in request.json:
        raise ApiError("no tags provided")

    tags = request.json["tags"]
    if type(tags) != list:
        raise ApiError("tags should be an array type")

    for tag in tags:
        group.add_tag(tag)

    group.save()

    data = {"data": group.to_dict(get_request_fields())}
    return json_response(data)


@groups_ctrl.route("/<group_id>/remove_tags", methods=["POST", "DELETE"])
@logged_action("group_remove_tags")
def remove_tags(group_id):
    from app.models import Group
    group = Group.get(group_id, GroupNotFound("group not found"))

    if not group.modification_allowed:
        raise Forbidden("You don't have permissions to modify this group")

    if not "tags" in request.json:
        raise ApiError("no tags provided")

    tags = request.json["tags"]
    if type(tags) != list:
        raise ApiError("tags should be an array type")

    for tag in tags:
        group.remove_tag(tag)

    group.save()

    data = {"data": group.to_dict(get_request_fields())}
    return json_response(data)
