from storable_model import StorableModel, now
from library.engine.utils import resolve_id
from library.engine.permutation import expand_pattern


class ApiAction(StorableModel):

    FIELDS = (
        "_id",
        "username",
        "action_type",
        "kwargs",
        "params",
        "computed",
        "status",
        "errors",
        "created_at",
        "updated_at",
    )

    REQUIRED_FIELDS = (
        "username",
        "action_type",
        "status",
        "created_at",
        "updated_at",
    )

    DEFAULTS = {
        "kwargs": {},
        "params": {},
        "computed": {},
        "created_at": now,
        "updated_at": now,
        "errors": []
    }

    REJECTED_FIELDS = (
        "created_at",
        "updated_at",
    )

    INDEXES = (
        "username",
        "action_type",
        "status",
        "created_at",
        "updated_at",
    )

    __slots__ = list(FIELDS)

    @classmethod
    def check_compute_handlers(cls):
        from library.engine.action_log import action_types
        failed_types = []
        for atype in action_types:
            if not hasattr(cls, "_compute_" + atype):
               failed_types.append(atype)
        return failed_types

    def _before_save(self):
        self.updated_at = now()
        if self._id is None:
            self._set_computed()

    def _compute_host_create(self):
        from app.models import Group, Datacenter
        host_fqdns = []
        fqdn_pattern = ""
        group_name = ""
        datacenter_name = ""
        if "fqdn" in self.params:
            host_fqdns = [self.params["fqdn"]]
        elif "fqdn_pattern" in self.params:
            fqdn_pattern = self.params["fqdn_pattern"]
            host_fqdns = list(expand_pattern(fqdn_pattern))
        if "group_id" in self.params:
            group = Group.get(self.params["group_id"])
            if group is not None:
                group_name = group.name
        if "datacenter_id" in self.params:
            dc = Datacenter.get(self.params["datacenter_id"])
            if dc is not None:
                datacenter_name = dc.name
        self.computed = {
            "host_fqdns": host_fqdns,
            "fqdn_pattern": fqdn_pattern,
            "group_name": group_name,
            "datacenter_name": datacenter_name
        }

    def _compute_host_delete(self):
        from app.models import Host
        host_fqdn = ""
        host = Host.get(self.kwargs["host_id"])
        if host is not None:
            host_fqdn = host.fqdn
        self.computed = {
            "host_fqdn": host_fqdn
        }

    def _compute_host_update(self):
        from app.models import Host, Group, Datacenter
        host_data = {}
        host_fqdn = ""
        if "host_id" in self.kwargs:
            host = Host.get(self.kwargs["host_id"])
            if host is not None:
                host_fqdn = host.fqdn
                for k, v in self.params.iteritems():
                    if k in Host.FIELDS:
                        old_value = getattr(host, k)
                        if v != old_value and unicode(v) != unicode(old_value):
                            host_data[k] = v
            if "group_id" in host_data:
                group_name = ""
                group = Group.get(host_data["group_id"])
                if group is not None:
                    group_name = group.name
                host_data["group_name"] = group_name
            if "datacenter_id" in host_data:
                datacenter_name = ""
                dc = Datacenter.get(host_data["datacenter_id"])
                if dc is not None:
                    datacenter_name = dc.name
                host_data["datacenter_name"] = datacenter_name

        self.computed = {
            "host_data": host_data,
            "host_fqdn": host_fqdn
        }

    def _compute_host_set_custom_fields(self):
        from app.models import Host
        host_fqdn = ""
        custom_fields_added = []
        custom_fields_replaced = []
        if "host_id" in self.kwargs:
            host = Host.get(self.kwargs["host_id"])
            if host is not None:
                host_fqdn = host.fqdn
                new_cfs = self.params.get("custom_fields")

                if new_cfs is not None:
                    if type(new_cfs) == dict:
                        new_cfs = [{"key": x[0], "value": x[1]} for x in new_cfs.iteritems()]

                    old_cfs_dict = dict([(x["key"], x["value"]) for x in host.custom_fields])
                    for item in new_cfs:
                        if item["key"] in old_cfs_dict:
                            old_value = old_cfs_dict[item["key"]]
                            new_value = item["value"]
                            if old_value != new_value:
                                custom_fields_replaced.append({
                                    "key": item["key"],
                                    "old_value": old_value,
                                    "new_value": new_value
                                })
                        else:
                            custom_fields_added.append(item)
        self.computed = {
            "host_fqdn": host_fqdn,
            "custom_fields_added": custom_fields_added,
            "custom_fields_replaced": custom_fields_replaced
        }

    def _compute_host_remove_custom_fields(self):
        from app.models import Host
        host_fqdn = ""
        custom_fields_removed = []
        if "host_id" in self.kwargs:
            host = Host.get(self.kwargs["host_id"])
            if host is not None:
                host_fqdn = host.fqdn
                cfs = self.params.get("custom_fields")
                old_cfs_dict = dict([(x["key"], x["value"]) for x in host.custom_fields])

                if cfs is not None:
                    if type(cfs) == dict:
                        cfs = [{"key": x} for x in cfs]

                    for item in cfs:
                        if item["key"] in old_cfs_dict:
                            custom_fields_removed.append({"key": item["key"], "value": old_cfs_dict[item["key"]]})
        self.computed = {
            "host_fqdn": host_fqdn,
            "custom_fields_removed": custom_fields_removed
        }

    def _compute_host_add_tags(self):
        from app.models import Host
        host_fqdn = ""
        tags_added = []
        if "host_id" in self.kwargs:
            host = Host.get(self.kwargs["host_id"])
            if host is not None:
                host_fqdn = host.fqdn
                tags = self.params.get("tags")
                if tags is not None:
                    for tag in tags:
                        if tag not in host.tags:
                            tags_added.append(tag)
        self.computed = {
            "host_fqdn": host_fqdn,
            "tags_added": tags_added
        }

    def _compute_host_remove_tags(self):
        from app.models import Host
        host_fqdn = ""
        tags_removed = []
        if "host_id" in self.kwargs:
            host = Host.get(self.kwargs["host_id"])
            if host is not None:
                host_fqdn = host.fqdn
                tags = self.params.get("tags")
                if tags is not None:
                    for tag in tags:
                        if tag in host.tags:
                            tags_removed.append(tag)
        self.computed = {
            "host_fqdn": host_fqdn,
            "tags_removed": tags_removed
        }

    def _compute_host_mass_move(self):
        from app.models import Host, Group
        group_name = ""
        hosts = Host.find({"_id": {"$in": [resolve_id(x) for x in self.params.get("host_ids", [])]}})
        host_fqdns = [x.fqdn for x in hosts]
        if "group_id" in self.params:
            group = Group.get(self.params.get("group_id", None))
            if group is not None:
                group_name = group.name
        self.computed = {
            "host_fqdns": host_fqdns,
            "group_name": group_name
        }

    def _compute_host_mass_delete(self):
        from app.models import Host
        hosts = Host.find({"_id": {"$in": [resolve_id(x) for x in self.params.get("host_ids", [])]}})
        host_fqdns = [x.fqdn for x in hosts]
        self.computed = {
            "host_fqdns": host_fqdns
        }

    def _compute_host_mass_detach(self):
        self._compute_host_mass_delete()

    def _compute_host_mass_set_datacenter(self):
        from app.models import Host, Datacenter
        datacenter_name = ""
        hosts = Host.find({"_id": {"$in": [resolve_id(x) for x in self.params.get("host_ids", [])]}})
        host_fqdns = [x.fqdn for x in hosts]
        if "datacenter_id" in self.params:
            dc = Datacenter.get(self.params.get("datacenter_id", None))
            if dc is not None:
                datacenter_name = dc.name
        self.computed = {
            "host_fqdns": host_fqdns,
            "datacenter_name": datacenter_name
        }

    def _compute_group_create(self):
        from app.models import WorkGroup
        group_name = ""
        work_group_name = ""
        if "name" in self.params:
            group_name = self.params["name"]
        if "work_group_id" in self.params:
            work_group = WorkGroup.get(self.params["work_group_id"])
            if work_group is not None:
                work_group_name = work_group.name

        self.computed = {
            "group_name": group_name,
            "work_group_name": work_group_name
        }

    def _compute_group_delete(self):
        from app.models import Group
        group_name = ""
        group = Group.get(self.kwargs["group_id"])
        if group is not None:
            group_name = group.name
        self.computed = {
            "group_name": group_name
        }

    def _compute_group_mass_delete(self):
        from app.models import Group
        groups = Group.find({"_id": {"$in": [resolve_id(x) for x in self.params.get("group_ids", [])]}})
        group_names = [x.name for x in groups]
        self.computed = {
            "group_names": group_names
        }

    def _compute_group_mass_move(self):
        from app.models import Group, WorkGroup
        groups = Group.find({"_id": {"$in": [resolve_id(x) for x in self.params.get("group_ids", [])]}})
        group_names = [x.name for x in groups]
        work_group_name = ""
        if "work_group_id" in self.params:
            work_group = WorkGroup.get(self.params["work_group_id"])
            if work_group is not None:
                work_group_name = work_group.name
        self.computed = {
            "group_names": group_names,
            "work_group_name": work_group_name
        }

    def _compute_group_set_children(self):
        from app.models import Group
        group_name = ""
        children = Group.find({"_id": {"$in": [resolve_id(x) for x in self.params.get("child_ids", [])]}})
        child_group_names = [x.name for x in children]
        group = Group.get(self.kwargs["group_id"])
        if group is not None:
            group_name = group.name
        self.computed = {
            "group_name": group_name,
            "child_group_names": child_group_names
        }

    def _compute_group_set_hosts(self):
        from app.models import Group, Host
        group_name = ""
        hosts = Host.find({"_id": {"$in": [resolve_id(x) for x in self.params.get("host_ids", [])]}})
        host_fqdns = [x.fqdn for x in hosts]
        group = Group.get(self.kwargs["group_id"])
        if group is not None:
            group_name = group.name
        self.computed = {
            "group_name": group_name,
            "host_fqdns": host_fqdns
        }

    def _compute_group_update(self):
        from app.models import Group, WorkGroup
        group_name = ""
        group_data = {}
        group = Group.get(self.kwargs["group_id"])
        if group is not None:
            group_name = group.name
            for k, v in self.params.iteritems():
                if k in Group.FIELDS:
                    old_value = getattr(group, k)
                    if v != old_value and unicode(v) != unicode(old_value):
                        group_data[k] = v
            if "work_group_id" in group_data:
                work_group_name = ""
                work_group = WorkGroup.get(group_data["work_group_id"])
                if work_group is not None:
                    work_group_name = work_group.name
                group_data["work_group_name"] = work_group_name
        self.computed = {
            "group_name": group_name,
            "group_data": group_data
        }


    def _compute_datacenter_create(self):
        from app.models import Datacenter
        datacenter_name = ""
        parent_name = ""
        if "name" in self.params:
            datacenter_name = self.params["name"]
        if "parent_id" in self.params:
            parent = Datacenter.get(self.params["parent_id"])
            if parent is not None:
                parent_name = parent.name
        self.computed = {
            "datacenter_name": datacenter_name,
            "parent_name": parent_name
        }

    def _compute_datacenter_delete(self):
        from app.models import Datacenter
        datacenter_name = ""
        dc = Datacenter.get(self.kwargs["dc_id"])
        if dc is not None:
            datacenter_name = dc.name
        self.computed = {
            "datacenter_name": datacenter_name
        }

    def _compute_datacenter_update(self):
        from app.models import Datacenter
        datacenter_name = ""
        datacenter_data = {}
        dc = Datacenter.get(self.kwargs["dc_id"])
        if dc is not None:
            datacenter_name = dc.name
            for k, v in self.params.iteritems():
                if k in Datacenter.FIELDS:
                    if k == "parent_id":
                        continue
                    old_value = getattr(dc, k)
                    if old_value != v and unicode(v) != unicode(old_value):
                        datacenter_data[k] = v
        self.computed = {
            "datacenter_name": datacenter_name,
            "datacenter_data": datacenter_data
        }

    def _compute_datacenter_set_parent(self):
        from app.models import Datacenter
        datacenter_name = ""
        parent_name = ""
        dc = Datacenter.get(self.kwargs["dc_id"])
        if dc is not None:
            datacenter_name = dc.name
        parent = Datacenter.get(self.params["parent_id"])
        if parent is not None:
            parent_name = parent.name
        self.computed = {
            "datacenter_name": datacenter_name,
            "parent_name": parent_name
        }

    def _compute_work_group_create(self):
        work_group_name = ""
        if "name" in self.params:
            work_group_name = self.params["name"]
        self.computed = {
            "work_group_name": work_group_name
        }

    def _compute_work_group_delete(self):
        from app.models import WorkGroup
        work_group_name = ""
        work_group = WorkGroup.get(self.kwargs["work_group_id"])
        if work_group is not None:
            work_group_name = work_group.name
        self.computed = {
            "work_group_name": work_group_name
        }

    def _compute_work_group_add_member(self):
        from app.models import WorkGroup, User
        work_group_name = ""
        user_name = ""
        work_group = WorkGroup.get(self.kwargs["work_group_id"])
        if work_group is not None:
            work_group_name = work_group.name
        if "user_id" in self.params:
            user = User.get(self.params["user_id"])
            if user is not None:
                user_name = user.name
        self.computed = {
            "work_group_name": work_group_name,
            "user_name": user_name
        }

    def _compute_work_group_remove_member(self):
        self._compute_work_group_add_member()

    def _compute_work_group_set_members(self):
        from app.models import WorkGroup, User
        work_group_name = ""
        members = User.find({"_id": {"$in": [resolve_id(x) for x in self.params.get("member_ids", [])]}})
        user_names = [x.username for x in members]
        work_group = WorkGroup.get(self.kwargs["work_group_id"])
        if work_group is not None:
            work_group_name = work_group.name
        self.computed = {
            "work_group_name": work_group_name,
            "user_names": user_names
        }

    def _compute_work_group_update(self):
        from app.models import WorkGroup
        work_group_name = ""
        work_group_data = {}
        work_group = WorkGroup.get(self.kwargs["work_group_id"])
        if work_group is not None:
            work_group_name = work_group.name
            for k, v in self.params.iteritems():
                if k in WorkGroup.FIELDS:
                    old_value = getattr(work_group, k)
                    if v != old_value and unicode(v) != unicode(old_value):
                        work_group_data[k] = v
        self.computed = {
            "work_group_name": work_group_name,
            "work_group_data": work_group_data
        }

    def _compute_work_group_switch_owner(self):
        from app.models import WorkGroup, User
        work_group_name = ""
        owner_username = ""
        work_group = WorkGroup.get(self.kwargs["work_group_id"])
        if work_group is not None:
            work_group_name = work_group.name
        if "owner_id" in self.params:
            owner = User.get(self.params["owner_id"])
            if owner is not None:
                owner_username = owner.username
        self.computed = {
            "work_group_name": work_group_name,
            "owner_username": owner_username
        }

    def _compute_network_group_create(self):
        network_group_name = ""
        if "name" in self.params:
            network_group_name = self.params["name"]
        self.computed = {
            "network_group_name": network_group_name
        }

    def _compute_network_group_delete(self):
        from app.models import NetworkGroup
        network_group_name = ""
        network_group = NetworkGroup.get(self.kwargs["network_group_id"])
        if network_group is not None:
            network_group_name = network_group.name
        self.computed = {
            "network_group_name": network_group_name
        }

    def _compute_user_create(self):
        username = ""
        if "username" in self.params:
            username = self.params["username"]
        self.computed = {
            "username": username
        }

    def _compute_user_set_password(self):
        from app.models import User
        username = ""
        user = User.get(self.kwargs["user_id"])
        if user is not None:
            username = user.username
        self.computed = {
            "username": username
        }

    def _compute_user_delete(self):
        self._compute_user_set_password()

    def _compute_user_set_supervisor(self):
        self._compute_user_set_password()

    def _compute_user_set_system(self):
        self._compute_user_set_password()

    def _compute_user_update(self):
        from app.models import User
        username = ""
        user_data = {}
        user = User.get(self.kwargs["user_id"])
        if user is not None:
            username = user.username
            for k, v in self.params.iteritems():
                if k.startswith("password"):
                    continue
                if k in User.FIELDS:
                    old_value = getattr(user, k)
                    if v != old_value and unicode(v) != unicode(old_value):
                        user_data[k] = v
        self.computed = {
            "username": username,
            "user_data": user_data
        }

    def _compute_group_set_custom_fields(self):
        from app.models import Group
        group_name = ""
        custom_fields_added = []
        custom_fields_replaced = []
        if "group_id" in self.kwargs:
            group = Group.get(self.kwargs["group_id"])
            if group is not None:
                group_name = group.name
                new_cfs = self.params.get("custom_fields")

                if new_cfs is not None:
                    if type(new_cfs) == dict:
                        new_cfs = [{"key": x[0], "value": x[1]} for x in new_cfs.iteritems()]

                    old_cfs_dict = dict([(x["key"], x["value"]) for x in group.custom_fields])
                    for item in new_cfs:
                        if item["key"] in old_cfs_dict:
                            old_value = old_cfs_dict[item["key"]]
                            new_value = item["value"]
                            if old_value != new_value:
                                custom_fields_replaced.append({
                                    "key": item["key"],
                                    "old_value": old_value,
                                    "new_value": new_value
                                })
                        else:
                            custom_fields_added.append(item)
        self.computed = {
            "group_name": group_name,
            "custom_fields_added": custom_fields_added,
            "custom_fields_replaced": custom_fields_replaced
        }

    def _compute_group_remove_custom_fields(self):
        from app.models import Group
        group_name = ""
        custom_fields_removed = []
        if "group_id" in self.kwargs:
            group = Group.get(self.kwargs["group_id"])
            if group is not None:
                group_name = group.name
                cfs = self.params.get("custom_fields")
                old_cfs_dict = dict([(x["key"], x["value"]) for x in group.custom_fields])

                if cfs is not None:
                    if type(cfs) == dict:
                        cfs = [{"key": x} for x in cfs]

                    for item in cfs:
                        if item["key"] in old_cfs_dict:
                            custom_fields_removed.append({"key": item["key"], "value": old_cfs_dict[item["key"]]})
        self.computed = {
            "group_name": group_name,
            "custom_fields_removed": custom_fields_removed
        }

    def _compute_group_add_tags(self):
        from app.models import Group
        group_name = ""
        tags_added = []
        if "group_id" in self.kwargs:
            group = Group.get(self.kwargs["group_id"])
            if group is not None:
                group_name = group.name
                tags = self.params.get("tags")
                if tags is not None:
                    for tag in tags:
                        if tag not in group.tags:
                            tags_added.append(tag)
        self.computed = {
            "group_name": group_name,
            "tags_added": tags_added
        }

    def _compute_group_remove_tags(self):
        from app.models import Group
        group_name = ""
        tags_removed = []
        if "group_id" in self.kwargs:
            group = Group.get(self.kwargs["group_id"])
            if group is not None:
                group_name = group.name
                tags = self.params.get("tags")
                if tags is not None:
                    for tag in tags:
                        if tag in group.tags:
                            tags_removed.append(tag)
        self.computed = {
            "group_name": group_name,
            "tags_removed": tags_removed
        }

    def _set_computed(self):
        method_name = "_compute_" + self.action_type
        if not hasattr(self, method_name):
            from app import app
            app.logger.info("Method %s is not implemented yet" % method_name)
            return
        method = getattr(self, method_name)
        method()
