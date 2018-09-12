from library.engine.errors import HostNotFound, Forbidden, GroupNotFound, DatacenterNotFound
from library.engine.utils import get_request_fields
from library.engine.action_log import logged_async_action


@logged_async_action("host_update")
def action_host_update(user_id, host_id, values, body):
    from app.models import Host, Group, Datacenter
    host = Host.get(host_id, HostNotFound("host not found"))

    if not host.modification_allowed_for(user_id):
        raise Forbidden("You don't have permissions to modify this host")

    host_attrs = dict([x for x in body.items() if x[0] in Host.FIELDS])

    if "group_id" in host_attrs and host_attrs["group_id"] is not None:
        group = Group.get(host_attrs["group_id"], GroupNotFound("group not found"))
        if not group.modification_allowed_for(user_id):
            raise Forbidden("You don't have permissions to move hosts to group %s" % group.name)
        host_attrs["group_id"] = group._id

    if "datacenter_id" in host_attrs and host_attrs["datacenter_id"] is not None:
        datacenter = Datacenter.get(host_attrs["datacenter_id"], DatacenterNotFound("datacenter not found"))
        host_attrs["datacenter_id"] = datacenter._id

    host.update(host_attrs)
    return { "data": host.to_dict(get_request_fields(values)) }


@logged_async_action("host_delete")
def action_host_delete(user_id, host_id, values):
    from app.models import Host
    host = Host.get(host_id, HostNotFound("host not found"))
    if not host.destruction_allowed_for(user_id):
        raise Forbidden("You don't have permission to modify this host")

    host.destroy()
    return { "data": host.to_dict(get_request_fields(values)) }