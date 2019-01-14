from unittest import TestCase
from library.engine.utils import merge, convert_keys

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

CK_INPUT = {
    "key0": "value0",
    "key1.key1_1.key1_1_1": "value1_1_1",
    "key1.key1_2": "value1_2",
    "key2.key1": "value_test"
}

CK_EXPECTED = {
    "key0": "value0",
    "key1": {
        "key1_1": {
            "key1_1_1": "value1_1_1",
        },
        "key1_2": "value1_2",
    },
    "key2": {
        "key1": "value_test"
    }
}


class TestMerge(TestCase):

    def test_merge_dicts(self):
        result = merge(D1, D2)
        self.assertDictEqual(result, EXPECTED)

    def test_convert_keys(self):
        self.assertDictEqual(convert_keys(CK_INPUT), CK_EXPECTED)
