from unittest import TestCase
from app.models import Datacenter as Base
from app.models.datacenter import DatacenterNotEmpty
from app.models.storable_model import FieldRequired, ParentCycle

TEST_COLLECTION = "tdatacenter"

class Datacenter(Base):
    _collection = TEST_COLLECTION


class TestDatacenterModel(TestCase):

    @classmethod
    def setUpClass(cls):
        Datacenter.ensure_indexes()

    def setUp(self):
        Datacenter.destroy_all()

    def tearDown(self):
        Datacenter.destroy_all()

    @classmethod
    def tearDownClass(cls):
        from library.db import db
        db.conn[TEST_COLLECTION].drop()

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

    def test_remove_from_parent_before_destroy(self):
        dc1 = Datacenter(name="dc1")
        dc1.save()
        dc12 = Datacenter(name="dc1.2")
        dc12.save()
        dc12.set_parent(dc1._id)
        dc12 = Datacenter.find_one({ "name": "dc1.2" })
        child_id = dc12._id
        dc12.destroy()
        dc1 = Datacenter.find_one({ "name": "dc1" })
        self.assertNotIn(child_id, dc1.child_ids)

    def test_all_children(self):
        dc1 = Datacenter(name="dc1")
        dc1.save()
        dc12 = Datacenter(name="dc1.2")
        dc12.save()
        dc12.set_parent(dc1)
        dc121 = Datacenter(name="dc1.2.1")
        dc121.save()
        dc121.set_parent(dc12)
        dc122 = Datacenter(name="dc1.2.2")
        dc122.save()
        dc122.set_parent(dc12)
        self.assertItemsEqual([dc12, dc121, dc122], dc1.get_all_children())

    def test_cycle(self):
        # DC1 -> DC1.2 -> DC1.2.1 -> DC1.2.1.3 --X--> DC1
        # the last connection must raise ParentCycle
        dc1 = Datacenter(name="dc1")
        dc1.save()
        dc12 = Datacenter(name="dc1.2")
        dc12.save()
        dc12.set_parent(dc1)
        dc121 = Datacenter(name="dc1.2.1")
        dc121.save()
        dc121.set_parent(dc12)
        dc1213 = Datacenter(name="dc1.2.1.3")
        dc1213.save()
        dc1213.set_parent(dc121)
        self.assertRaises(ParentCycle, dc1.set_parent, dc1213)
        self.assertRaises(ParentCycle, dc1213.add_child, dc1)