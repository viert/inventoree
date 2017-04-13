from commands import Command
from library.engine.utils import get_modules
import importlib
import os.path
from app.models.storable_model import ModelMeta

class Index(Command):
    def run(self):
        from app import app
        app.logger.info("Creating indexes")
        models_directory = os.path.join(app.BASE_DIR, "app/models")
        modules = [x for x in get_modules(models_directory) if x != "storable_model"]
        for mname in modules:
            module = importlib.import_module("app.models.%s" % mname)
            for attr in dir(module):
                if attr.startswith("__") or attr == 'StorableModel':
                    continue
                obj = getattr(module, attr)
                if hasattr(obj, "ensure_indexes"):
                    app.logger.info("Creating indexes for %s" % attr)
                    obj.ensure_indexes()
        from library.db import db
        app.logger.info("Creating sessions indexes")
        db.conn["sessions"].create_index("sid", unique=True, sparse=False)