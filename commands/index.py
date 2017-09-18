from commands import Command
from library.engine.utils import get_modules
import importlib
import os.path


class Index(Command):

    def init_argument_parser(self, parser):
        parser.add_argument("-w", "--overwrite", dest="overwrite", action="store_true", default=False,
                            help="Overwrite existing indexes in case of conflicts")

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
                    app.logger.info("Creating indexes for %s, collection %s" % (attr, obj.collection))
                    obj.ensure_indexes(True, self.args.overwrite)
        from library.db import db
        app.logger.info("Creating sessions indexes")
        db.conn["sessions"].create_index("sid", unique=True, sparse=False)