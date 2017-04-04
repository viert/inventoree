from app.models.storable_model import StorableModel, \
    ParentDoesNotExist, ParentAlreadyExists,\
    ChildAlreadyExists, ChildDoesNotExist, now, save_required

from bson.objectid import ObjectId


class GroupNotFound(Exception):
    pass


class GroupNotEmpty(Exception):
    pass


class InvalidProjectId(Exception):
    pass


class Group(StorableModel):

    _collection = 'groups'

    FIELDS = (
        "_id",
        "name",
        "description",
        "created_at",
        "updated_at",
        "project_id",
        "parent_ids",
        "child_ids",
    )

    DEFAULTS = {
        "created_at": now,
        "updated_at": now,
        "parent_ids": [],
        "child_ids": []
    }

    REQUIRED_FIELDS = (
        "project_id",
        "parent_ids",
        "child_ids",
        "name"
    )

    INDEXES = (
        "parent_ids",
        "child_ids",
        "name"
    )

    __slots__ = FIELDS

    @staticmethod
    def _resolve_group(group):
        # gets group or group_id or str with group_id
        # and return a tuple of actual (group, group_id)
        if type(group) == Group:
            group_id = group._id
        elif type(group) == ObjectId:
            group_id = group
            group = Group.find_one({ "_id": group_id })
        else:
            group_id = ObjectId(group)
            group = Group.find_one({ "_id": group_id })
        if group is None:
            raise GroupNotFound("Group %s not found" % group_id)
        return group, group_id

    @save_required
    def add_parent(self, parent):
        parent, parent_id = self._resolve_group(parent)
        if parent_id in self.parent_ids:
            raise ParentAlreadyExists("Group %s is already a parent of group %s" % (parent.name, self.name))
        parent.child_ids.append(self._id)
        self.parent_ids.append(parent._id)
        parent.save()
        self.save()

    @save_required
    def remove_parent(self, parent):
        parent, parent_id = self._resolve_group(parent)
        if parent_id not in self.parent_ids:
            raise ParentDoesNotExist("Group %s is not a parent of group %s" % (parent.name, self.name))
        parent.child_ids.remove(self._id)
        self.parent_ids.remove(parent._id)
        parent.save()
        self.save()

    @save_required
    def add_child(self, child):
        child, child_id = self._resolve_group(child)
        if child_id in self.child_ids:
            raise ChildAlreadyExists("Group %s is already a child of group %s" % (child.name, self.name))
        child.parent_ids.append(self._id)
        self.child_ids.append(child._id)
        child.save()
        self.save()

    @save_required
    def remove_child(self, child):
        child, child_id = self._resolve_group(child)
        if child_id not in self.child_ids:
            raise ChildDoesNotExist("Group %s is not a child of group %s" % (child.name, self.name))
        child.parent_ids.remove(self._id)
        self.child_ids.remove(child._id)
        child.save()
        self.save()

    def hosts(self):
        # Placeholder
        return []

    @property
    def empty(self):
        return len(self.child_ids) + len(self.hosts()) == 0

    @property
    def parents(self):
        return Group.find({ "_id": { "$in": self.parent_ids }})

    @property
    def children(self):
        return Group.find({ "_id": { "$in": self.child_ids }})

    @property
    def project(self):
        from app.models import Project
        return Project.find_one({ "_id": self.project_id })

    def touch(self):
        self.updated_at = now()

    def _before_save(self):
        from app.models import Project
        p = Project.find_one({ "_id": self.project_id })
        if p is None:
            raise InvalidProjectId("Project with id %s doesn't exist" % self.project_id)
        self.touch()

    def _before_delete(self):
        if not self.empty:
            raise GroupNotEmpty()


