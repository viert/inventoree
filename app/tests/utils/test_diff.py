from unittest import TestCase
from library.engine.utils import diff

class TestDiff(TestCase):

    def test_diff(self):
        original = [1,3,7,9,12]
        updated = [3,7,9,14]
        d = diff(original, updated)
        self.assertItemsEqual([1,12], d.remove)
        self.assertItemsEqual([14], d.add)

    def test_equal(self):
        original = [1,3,7,9,12]
        updated = [1,3,7,9,12]
        d = diff(original, updated)
        self.assertItemsEqual([], d.add)
        self.assertItemsEqual([], d.remove)
