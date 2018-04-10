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
                        if v != old_value and str(v) != str(old_value):
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
            "host": host_data,
            "host_fqdn": host_fqdn
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
        from app.models import Project
        group_name = ""
        project_name = ""
        if "name" in self.params:
            group_name = self.params["name"]
        if "project_id" in self.params:
            project = Project.get(self.params["project_id"])
            if project is not None:
                project_name = project.name

        self.computed = {
            "group_name": group_name,
            "project_name": project_name
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
        from app.models import Group, Project
        groups = Group.find({"_id": {"$in": [resolve_id(x) for x in self.params.get("group_ids", [])]}})
        group_names = [x.name for x in groups]
        project_name = ""
        if "project_id" in self.params:
            project = Project.get(self.params["project_id"])
            if project is not None:
                project_name = project.name
        self.computed = {
            "group_names": group_names,
            "project_name": project_name
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
        from app.models import Group, Project
        group_name = ""
        group_data = {}
        group = Group.get(self.kwargs["group_id"])
        if group is not None:
            group_name = group.name
            for k, v in self.params.iteritems():
                if k in Group.FIELDS:
                    old_value = getattr(group, k)
                    if v != old_value and str(v) != str(old_value):
                        group_data[k] = v
            if "project_id" in group_data:
                project_name = ""
                project = Project.get(group_data["project_id"])
                if project is not None:
                    project_name = project.name
                group_data["project_name"] = project_name
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
                    if old_value != v and str(v) != str(old_value):
                        datacenter_data[k] = v
        self.computed = {
            "datacenter_name": datacenter_name,
            "datacenter": datacenter_data
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

    def _set_computed(self):
        method_name = "_compute_" + self.action_type
        if not hasattr(self, method_name):
            from app import app
            app.logger.info("Method %s is not implemented yet" % method_name)
            return
        method = getattr(self, method_name)
        method()
