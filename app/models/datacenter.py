from app.models.storable_model import StorableModel, ParentDoesNotExist,\
    ParentAlreadyExists, ParentCycle, ObjectSaveRequired, \
    ChildDoesNotExist, ChildAlreadyExists, save_required, now
from bson.objectid import ObjectId


class DatacenterNotFound(Exception):
    pass


class DatacenterNotEmpty(Exception):
    pass


class Datacenter(StorableModel):

    _host_class = None

    FIELDS = (
        "_id",
        "name",
        "human_readable",
        "parent_id",
        "root_id",
        "child_ids",
        "created_at",
        "updated_at",
    )

    KEY_FIELD = "name"
    
    REQUIRED_FIELDS = (
        "name",
        "created_at",
        "updated_at",
    )

    DEFAULTS = {
        "child_ids": [],
        "created_at": now,
        "updated_at": now
    }

    INDEXES = (
        ["name", { "unique": True }],
        "parent_id",
        "root_id",
    )

    REJECTED_FIELDS = (
        "parent_id",
        "root_id",
        "child_ids",
        "created_at",
        "updated_at"
    )

    __slots__ = FIELDS
    
    @classmethod
    def _resolve_dc(cls, dc):
        # gets datacenter or datacenter_id or str with datacenter_id
        # and return a tuple of actual (datacenter, datacenter_id)
        if type(dc) == cls:
            dc_id = dc._id
            if dc_id is None:
                raise ObjectSaveRequired("%s must be saved first" % dc)
        elif type(dc) == ObjectId:
            dc_id = dc
            dc = cls.find_one({ "_id": dc_id })
        else:
            dc_id = ObjectId(dc)
            dc = cls.find_one({ "_id": dc_id })
        if dc is None:
            raise DatacenterNotFound("Datacenter %s not found" % dc_id)
        return dc, dc_id

    @save_required
    def set_parent(self, parent):
        if self.parent_id is not None:
            raise ParentAlreadyExists("You should unset current parent first")
        parent, parent_id = self._resolve_dc(parent)
        if parent is None:
            raise ParentDoesNotExist("Parent with id %s doesn't exist" % parent_id)
        if parent._id == self._id:
            raise ParentCycle("Can't set parent to myself")
        if parent in self.get_all_children():
            raise ParentCycle("Can't set one of (grand)children parent")
        parent.child_ids.append(self._id)
        self.parent_id = parent_id
        parent.save()
        self.save()

    @save_required
    def unset_parent(self):
        if self.parent_id is None:
            raise ParentDoesNotExist("This object doesn't have a parent")
        parent = self.parent
        parent.child_ids.remove(self._id)
        self.parent_id = None
        self.save()
        parent.save()

    @save_required
    def add_child(self, child):
        child, child_id = self._resolve_dc(child)
        if child is None:
            raise ChildDoesNotExist("Child with id %s doesn't exist" % child_id)
        if child.parent_id is not None:
            raise ParentAlreadyExists("This child already have a parent")
        if child_id == self._id:
            raise ParentCycle("Can't make datacenter child of itself")
        if self in child.get_all_children():
            raise ParentCycle("Can't add on of (grand)parents as child")
        if child_id in self.child_ids:
            raise ChildAlreadyExists("%s is already a child of %s" (child, self))
        self.child_ids.append(child_id)
        child.parent_id = self._id
        child.save()
        self.save()

    @save_required
    def remove_child(self, child):
        child, child_id = self._resolve_dc(child)
        if child is None:
            raise ChildDoesNotExist("Child with id %s doesn't exist" % child_id)
        self.child_ids.remove(child_id)
        child.parent_id = None
        child.save()
        self.save()

    def get_all_children(self):
        children = self.children[:]
        for child in self.children:
            children += child.get_all_children()
        return children

    def touch(self):
        self.updated_at = now()

    @property
    def parent(self):
        return self.__class__.find_one({ "_id": self.parent_id })

    @property
    def root(self):
        return self.__class__.find_one({ "_id": self.root_id })

    @save_required
    def _detect_root_id(self):
        if self.parent_id is None:
            return self._id
        else:
            return self.parent._detect_root_id()

    def _before_save(self):
        if not self.is_new:
            root_id = self._detect_root_id()
            if root_id == self._id:
                root_id = None
            self.root_id = root_id
        else:
            # set parent_id only via set_parent
            self.parent_id = None
        self.touch()

    def _before_delete(self):
        if len(self.child_ids) > 0:
            raise DatacenterNotEmpty("Can not delete datacenter because it's not empty")
        if self.parent is not None:
            self.unset_parent()
        self.host_class.unset_datacenter(self._id)

    @property
    def children(self):
        return self.__class__.find({ "_id": { "$in": self.child_ids } }).all()

    @property
    @save_required
    def is_root(self):
        return self.root_id is None

    @property
    def host_class(self):
        if self._host_class is None:
            from app.models import Host
            self.__class__._host_class = Host
        return self._host_class

    @property
    def hosts(self):
        return self.host_class.find({ "datacenter_id": self._id })

    @property
    def all_hosts(self):
        all_ids = [self._id] + [x._id for x in self.get_all_children()]
        return self.host_class.find({ "datacenter_id": { "$in": all_ids } })