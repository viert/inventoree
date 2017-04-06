from unittest import TestCase
from app.models import Datacenter as Base
from app.models.datacenter import DatacenterNotEmpty
from app.models.storable_model import FieldRequired

class Datacenter(Base):
    _collection = 'tdatacenter'


class TestDatacenterModel(TestCase):

    def setUp(self):
        Datacenter.destroy_all()

    def tearDown(self):
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

    def test_destroy_non_empty(self):
        dc1 = Datacenter(name="dc1")
        dc1.save()
        dc12 = Datacenter(name="dc1.2")
        dc12.save()
        dc1.add_child(dc12)
        self.assertRaises(DatacenterNotEmpty, dc1.destroy)

    def test_add_child_by_object(self):
        dc1 = Datacenter(name="dc1")
        dc1.save()
        dc12 = Datacenter(name="dc1.2")
        dc12.save()
        dc1.add_child(dc12)
        dc1 = Datacenter.find_one({ "name": "dc1" })
        dc12 = Datacenter.find_one({ "name": "dc1.2" })
        self.assertIn(dc12._id, dc1.child_ids)
        self.assertEqual(dc12.parent_id, dc1._id)

    def test_add_child_by_id(self):
        dc1 = Datacenter(name="dc1")
        dc1.save()
        dc12 = Datacenter(name="dc1.2")
        dc12.save()
        dc1.add_child(dc12._id)
        dc1 = Datacenter.find_one({ "name": "dc1" })
        dc12 = Datacenter.find_one({ "name": "dc1.2" })
        self.assertIn(dc12._id, dc1.child_ids)
        self.assertEqual(dc12.parent_id, dc1._id)

    def test_set_parent_by_object(self):
        dc1 = Datacenter(name="dc1")
        dc1.save()
        dc12 = Datacenter(name="dc1.2")
        dc12.save()
        dc12.set_parent(dc1)
        dc1 = Datacenter.find_one({ "name": "dc1" })
        dc12 = Datacenter.find_one({ "name": "dc1.2" })
        self.assertIn(dc12._id, dc1.child_ids)
        self.assertEqual(dc12.parent_id, dc1._id)

    def test_set_parent_by_id(self):
        dc1 = Datacenter(name="dc1")
        dc1.save()
        dc12 = Datacenter(name="dc1.2")
        dc12.save()
        dc12.set_parent(dc1._id)
        dc1 = Datacenter.find_one({ "name": "dc1" })
        dc12 = Datacenter.find_one({ "name": "dc1.2" })
        self.assertIn(dc12._id, dc1.child_ids)
        self.assertEqual(dc12.parent_id, dc1._id)
