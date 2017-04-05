from unittest import TestCase
from app.models import Datacenter
from app.models.storable_model import FieldRequired


class TestDatacenterModel(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.dc1 = Datacenter(name="dc1")
        cls.dc1.save()

        cls.dc11 = Datacenter(name="dc1.1")
        cls.dc11.save()
        cls.dc1.add_child(cls.dc11)

        cls.dc12 = Datacenter(name="dc1.2")
        cls.dc12.save()
        cls.dc12.set_parent(cls.dc1)

        cls.dc121 = Datacenter(name="dc1.2.1")
        cls.dc121.save()
        cls.dc122 = Datacenter(name="dc1.2.2")
        cls.dc122.save()

        cls.dc12.add_child(cls.dc121)
        cls.dc12.add_child(cls.dc122)

    @classmethod
    def tearDownClass(cls):
        cls.dc121.unset_parent()
        cls.dc121.destroy()
        cls.dc122.unset_parent()
        cls.dc122.destroy()
        cls.dc12.unset_parent()
        cls.dc12.destroy()
        cls.dc11.unset_parent()
        cls.dc11.destroy()
        cls.dc1.destroy()

    def test_incomlete(self):
        dc = Datacenter()
        self.assertRaises(FieldRequired, dc.save)

