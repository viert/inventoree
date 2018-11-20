from unittest import TestCase
from app.models import User, Group, WorkGroup, Host
from library.engine.ownership import user_groups, user_work_groups, user_hosts


class TestOwnership(TestCase):

    user1 = None
    user2 = None
    wg1 = None
    wg2 = None

    groups = {}
    hosts = []

    @classmethod
    def setUpClass(cls):
        cls.user1 = User(username="user1").save()
        cls.user2 = User(username="user2").save()
        cls.wg1 = WorkGroup(name="wg1", owner_id=cls.user1._id).save()
        cls.wg2 = WorkGroup(name="wg2", owner_id=cls.user2._id).save()
        cls.groups["g11"] = Group(name="g11", work_group_id=cls.wg1._id).save()
        cls.groups["g12"] = Group(name="g12", work_group_id=cls.wg1._id).save()
        cls.groups["g21"] = Group(name="g21", work_group_id=cls.wg2._id).save()
        cls.groups["g22"] = Group(name="g22", work_group_id=cls.wg2._id).save()
        cls.hosts.append(Host(fqdn="host1", group_id=cls.groups["g11"]._id).save())
        cls.hosts.append(Host(fqdn="host2", group_id=cls.groups["g11"]._id).save())
        cls.hosts.append(Host(fqdn="host3", group_id=cls.groups["g12"]._id).save())
        cls.hosts.append(Host(fqdn="host4", group_id=cls.groups["g12"]._id).save())
        cls.hosts.append(Host(fqdn="host5", group_id=cls.groups["g21"]._id).save())
        cls.hosts.append(Host(fqdn="host6", group_id=cls.groups["g21"]._id).save())
        cls.hosts.append(Host(fqdn="host7", group_id=cls.groups["g22"]._id).save())
        cls.hosts.append(Host(fqdn="host8", group_id=cls.groups["g22"]._id).save())
        cls.hosts.append(Host(fqdn="host9").save())
        cls.hosts.append(Host(fqdn="host10").save())

    def test_user_work_groups(self):
        wgs = user_work_groups(self.user1._id).all()
        self.assertEqual(1, len(wgs))
        ids = [x._id for x in wgs]
        self.assertItemsEqual(ids, [self.wg1._id])

        wgs = user_work_groups(self.user2._id).all()
        self.assertEqual(1, len(wgs))
        ids = [x._id for x in wgs]
        self.assertItemsEqual(ids, [self.wg2._id])

    def test_user_groups(self):
        wgs = user_groups(self.user1._id).all()
        self.assertEqual(2, len(wgs))
        ids = [x._id for x in wgs]
        self.assertItemsEqual(ids, [
            self.groups["g11"]._id,
            self.groups["g12"]._id,
        ])

        wgs = user_groups(self.user2._id).all()
        self.assertEqual(2, len(wgs))
        ids = [x._id for x in wgs]
        self.assertItemsEqual(ids, [
            self.groups["g21"]._id,
            self.groups["g22"]._id,
        ])

    def test_user_hosts(self):
        hsts = user_hosts(self.user1._id, include_not_assigned=False).all()
        self.assertEqual(4, len(hsts))
        ids = list(set([x.group_id for x in hsts]))
        self.assertItemsEqual(ids, [self.groups["g11"]._id, self.groups["g12"]._id])

        hsts = user_hosts(self.user2._id, include_not_assigned=True).all()
        self.assertEqual(6, len(hsts))
        ids = list(set([x.group_id for x in hsts]))
        self.assertItemsEqual(ids, [self.groups["g21"]._id, self.groups["g22"]._id, None])

    @classmethod
    def tearDownClass(cls):
        User.destroy_all()