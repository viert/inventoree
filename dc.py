from app.models import Datacenter

Datacenter.destroy_all()
dc1 = Datacenter(name="dc1")
dc11 = Datacenter(name="dc1.1")
dc1.save()
dc11.save()
dc1.add_child(dc11)

dc12 = Datacenter(name="dc1.2")
dc121 = Datacenter(name="dc1.2.1")
dc122 = Datacenter(name="dc1.2.2")

dc1.add_child(dc12)

dc12.save()
dc121.save()
dc122.save()

dc121.set_parent(dc12)
dc122.set_parent(dc12)