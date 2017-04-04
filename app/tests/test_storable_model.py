from unittest import TestCase
from app.models.storable_model import StorableModel, FieldRequired
from datetime import datetime
import warnings

CALLABLE_DEFAULT_VALUE = 4

def callable_default():
    return CALLABLE_DEFAULT_VALUE

class TestModel(StorableModel):

    FIELDS = (
        '_id',
        'field1',
        'field2',
        'field3',
        'callable_default_field'
    )

    DEFAULTS = {
        'field1': 'default_value',
        'field3': 'required_default_value',
        'callable_default_field': callable_default
    }

    REQUIRED_FIELDS = (
        'field2',
        'field3',
    )

    # Incorrect: not a tuple!!!
    INDEXES = (
        "field1"
    )

    __slots__ = FIELDS

class TestStorableModel(TestCase):
    def test_init(self):
        self.assertRaises(AttributeError, TestModel, nosuchfield='value')
        model = TestModel(field1='value')
        self.assertFalse(hasattr(model, '__dict__'), msg='StorableModel is not a slots class')
        self.assertEqual(model.field1, 'value')
        model._before_delete()
        model._before_save()


    def test_incomplete(self):
        model = TestModel(field1='value')
        self.assertRaises(FieldRequired, model.save)

    def test_incorrect_index(self):
        model = TestModel()
        self.assertRaises(TypeError, model.ensure_indexes)