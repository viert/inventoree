from app.models.storable_model import StorableModel, ParentDoesNotExist,\
    ParentAlreadyExists,\
    ChildDoesNotExist, save_required
from bson.objectid import ObjectId

class DatacenterNotFound(Exception):
    pass


class Datacenter(StorableModel):

    FIELDS = (
        "_id",
        "name",
        "parent_id",
        "root_id",
        "child_ids"
    )
    
    REQUIRED_FIELDS = (
        "name",
    )

    INDEXES = (
        "name",
        "parent_id",
        "root_id",
    )

    __slots__ = FIELDS
    
    @staticmethod
    def _resolve_dc(dc):
        # gets datacenter or datacenter_id or str with datacenter_id
        # and return a tuple of actual (datacenter, datacenter_id)
        if type(dc) == Datacenter:
            dc_id = dc._id
        elif type(dc) == ObjectId:
            dc_id = dc
            dc = Datacenter.find_one({ "_id": dc_id })
        else:
            dc_id = ObjectId(dc)
            dc = Datacenter.find_one({ "_id": dc_id })
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
        parent.child_ids.append(self._id)
        self.parent_id = parent_id
        parent.save()
        self.save()

    @save_required
    def unset_parent(self):
        if self.parent_id is None:
            raise ParentDoesNotExist("This object doesn't have a parent")
        self.parent.child_ids.remove(self._id)
        self.parent_id = None
        self.save()
        self.parent.save()

    @save_required
    def add_child(self, child):
        child, child_id = self._resolve_dc(child)
        if child is None:
            raise ChildDoesNotExist("Child with id %s doesn't exist" % child_id)
        if child.parent_id is not None:
            raise ParentAlreadyExists("This child already have a parent")
        self.child_ids.append(child_id)
        child.parent_id = self._id
        child.save()
        self.save()

    @save_required
    def remove_child(self, child):
        child, child_id = self._resolve_dc(child)
        if child is None:
            raise ChildDoesNotExist("Child with id %s doesn't exist" % child_id)
        child.unset_parent()

    @property
    def parent(self):
        return Datacenter.find_one({ "_id": self.parent_id })

    @save_required
    def detect_root_id(self):
        if self.parent_id is None:
            return self._id
        else:
            return self.parent.detect_root_id()

    def _before_save(self):
        if not self.is_new:
            root_id = self.detect_root_id
            if root_id == self._id:
                root_id = None
            self.root_id = root_id

    @property
    @save_required
    def is_root(self):
        return self.root_id is None