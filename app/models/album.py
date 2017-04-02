from storable_model import StorableModel

class Album(StorableModel):

    FIELDS = [
        'name',
        'year'
    ]

    REQUIRED_FIELDS = [
        'name'
    ]

    INDEXES = [
        "name",
    ]