from app.models.storable_model import StorableModel, \
    ParentDoesNotExist, ParentAlreadyExists,\
    ChildAlreadyExists, ChildDoesNotExist,\
    ParentCycle, now, save_required
from app.models import Project

from bson.objectid import ObjectId


class GroupNotFound(Exception):
    pass


class GroupNotEmpty(Exception):
    pass


class InvalidProjectId(Exception):
    pass


class Group(StorableModel):

    _collection = 'groups'
    _project_class = Project

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

    @classmethod
    def _resolve_group(cls, group):
        # gets group or group_id or str with group_id
        # and return a tuple of actual (group, group_id)
        if type(group) == cls:
            group_id = group._id
        elif type(group) == ObjectId:
            group_id = group
            group = cls.find_one({ "_id": group_id })
        else:
            group_id = ObjectId(group)
            group = cls.find_one({ "_id": group_id })
        if group is None:
            raise GroupNotFound("Group %s not found" % group_id)
        return group, group_id

    @save_required
    def add_parent(self, parent):
        parent, parent_id = self._resolve_group(parent)
        if parent_id in self.parent_ids:
            raise ParentAlreadyExists("Group %s is already a parent of group %s" % (parent.name, self.name))
        if parent_id == self._id:
            raise ParentCycle("Can't make group parent of itself")
        if self in parent.get_all_parents():
            raise ParentCycle("Can't add one of (grand)child group as a parent")
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
        if child_id == self._id:
            raise ParentCycle("Can't make group child of itself")
        if self in child.get_all_children():
            raise ParentCycle("Can't add one of (grand)parent group as a child")
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
        return self.__class__.find({ "_id": { "$in": self.parent_ids }}).all()

    @property
    def children(self):
        return self.__class__.find({ "_id": { "$in": self.child_ids }}).all()

    @property
    def project(self):
        return self._project_class.find_one({ "_id": self.project_id })

    def get_all_children(self):
        children = self.children[:]
        for child in self.children:
            children += child.get_all_children()
        return children

    def get_all_parents(self):
        parents = self.parents[:]
        for parent in self.parents:
            parents += parent.get_all_parents()
        return parents

    def touch(self):
        self.updated_at = now()

    def _before_save(self):
        p = self._project_class.find_one({ "_id": self.project_id })
        if p is None:
            raise InvalidProjectId("Project with id %s doesn't exist" % self.project_id)
        self.touch()

    def _before_delete(self):
        if not self.empty:
            raise GroupNotEmpty()


