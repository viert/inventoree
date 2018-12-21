from unittest import TestCase
from library.engine.utils import merge

D1 = {
    "field1": 3,
    "field2": "a",
    "field3": [1, 3, 5],
    "field4": {
        "field5": {
            "field6": "hello"
        }
    }
}

D2 = {
    "field1": {
        "override": "yes"
    },
    "field3": [9, 7, 4],
    "field4": {
        "field5": {
            "field7": {
                "new_data": True
            }
        }
    },
    "field8": "bye"
}

EXPECTED = {
    "field1": {
        "override": "yes"
    },
    "field2": "a",
    "field3": [9, 7, 4],
    "field4": {
        "field5": {
            "field6": "hello",
            "field7": {
                "new_data": True
            }
        }
    },
    "field8": "bye"
}


class TestMerge(TestCase):

    def test_merge_dicts(self):
        result = merge(D1, D2)
        self.assertDictEqual(result, EXPECTED)
