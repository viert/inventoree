from unittest import TestCase
from app.models import Datacenter as Base
from app.models.storable_model import FieldRequired

class Datacenter(Base):
    _collection = 'tdatacenter'


class TestDatacenterModel(TestCase):

    @classmethod
    def setUpClass(cls):
        Datacenter.destroy_all()

    @classmethod
    def tearDownClass(cls):
        Datacenter.destroy_all()

    def test_incomlete(self):
        dc = Datacenter()
        self.assertRaises(FieldRequired, dc.save)

    def test_children_before_save(self):
        from app.models.storable_model import ObjectSaveRequired
        dc1 = Datacenter(name="dc1")
        dc12 = Datacenter(name="dc1.2")
        self.assertRaises(ObjectSaveRequired, dc1.add_child, dc12)
        self.assertRaises(ObjectSaveRequired, dc12.set_parent, dc1)

    def test_self_parent(self):
        from app.models.storable_model import ParentCycle
        dc1 = Datacenter(name="dc1")
        dc1.save()
        self.assertRaises(ParentCycle, dc1.set_parent, dc1._id)
        self.assertRaises(ParentCycle, dc1.set_parent, dc1)
        dc1.destroy()