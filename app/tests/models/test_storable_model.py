from unittest import TestCase
from app.models.storable_model import StorableModel, FieldRequired

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

    REJECTED_FIELDS = (
        'field1',
    )

    # Incorrect: not a tuple!!!
    INDEXES = (
        "field1"
    )

    __slots__ = FIELDS


class TestStorableModel(TestCase):

    def setUp(self):
        TestModel.destroy_all()

    def tearDown(self):
        TestModel.destroy_all()

    def test_init(self):
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

    def test_eq(self):
        model = TestModel(field2="mymodel")
        model.save()
        model2 = TestModel.find_one({ "field2": "mymodel" })
        self.assertEqual(model, model2)

    def test_reject_on_update(self):
        model = TestModel(field1="original_value", field2="mymodel_reject_test")
        model.save()
        id = model._id
        model.update({ "field1": "new_value" })
        model = TestModel.find_one({ "_id": id })
        self.assertEqual(model.field1, "original_value")

    def test_update(self):
        model = TestModel(field1="original_value", field2="mymodel_update_test")
        model.save()
        id = model._id
        model.update({ "field2": "mymodel_updated" })
        model = TestModel.find_one({ "_id": id })
        self.assertEqual(model.field2, "mymodel_updated")
