import os
import os.path
import sys
import importlib
import logging
from flask import Flask, request, session
from collections import namedtuple
from library.engine.utils import get_py_files
from library.engine.json_encoder import MongoJSONEncoder
from library.mongo_session import MongoSessionInterface
from werkzeug.contrib.cache import MemcachedCache, SimpleCache


class BaseApp(object):

    DEFAULT_LOG_FORMAT = "[%(asctime)s] %(levelname)s %(filename)s:%(lineno)d %(message)s"
    DEFAULT_LOG_LEVEL = "debug"
    CTRL_MODULES_PREFIX = "app.controllers"

    def __init__(self):
        import inspect
        class_file = inspect.getfile(self.__class__)
        print class_file
        self.APP_DIR = os.path.dirname(os.path.abspath(class_file))
        self.BASE_DIR = os.path.abspath(os.path.join(self.APP_DIR, "../"))
        self.__read_config()
        self.__prepare_logger()
        self.__prepare_flask()
        self.__set_cache()

    def __set_cache(self):
        self.logger.debug("Setting up the cache")
        if hasattr(self.config, 'cache') and "MEMCACHE_BACKENDS" in self.config.cache:
            self.cache = MemcachedCache(self.config.cache["MEMCACHE_BACKENDS"])
        else:
            self.cache = SimpleCache()

    def __set_csrf_protection(self):
        if 'CSRF_PROTECTION' in self.config.app and self.config.app['CSRF_PROTECTION']:
            from library.engine.utils import json_response
            # CSRF Protection
            @self.flask.before_request
            def csrf_protect():
                if request.method != "GET":
                    token = session.get('_csrf_token', None)
                    if not token or token != request.form.get('_csrf_token'):
                        return json_response({'errors': ['request is not authorized: csrf token is invalid']}, 403)

    def __prepare_flask(self):
        self.logger.debug("Creating flask app")
        static_folder = self.config.http.get("STATIC", "static")
        static_folder = os.path.abspath(os.path.join(self.BASE_DIR, static_folder))
        self.flask = Flask(__name__, static_folder=static_folder)
        self.flask.json_encoder = MongoJSONEncoder
        self.logger.debug("Setting sessions interface")
        self.flask.session_interface = MongoSessionInterface(collection_name='sessions')

        self.logger.info("Loading routes...")
        for route in self.config.http["ROUTES"]:
            if not "controller" in route:
                self.logger.error("Invalid route %s: no controller found" % route)
                continue
            if not "prefix" in route:
                self.logger.error("Invalid route %s: no prefix found" % route)
                continue

            module_name = "%s.%s" % (self.CTRL_MODULES_PREFIX, route["controller"])
            blueprint_name = route["controller"].split(".")[-1] + "_ctrl"
            self.logger.info("Loading controller '%s' from module %s" % (blueprint_name, module_name))
            try:
                module = importlib.import_module(module_name)
            except ImportError as e:
                self.logger.error("Error loading controller module %s: %s" % (module_name, e))
                continue
            try:
                blueprint = getattr(module, blueprint_name)
            except AttributeError:
                self.logger.error("No blueprint named %s found in module %s" % (blueprint_name, module_name))
                continue
            self.flask.register_blueprint(blueprint, url_prefix=route["prefix"])
            self.logger.info("Registered blueprint '%s' with url_prefix=%s" % (blueprint_name, route["prefix"]))

    def __read_config(self):
        # reading and compiling config files
        config_directory = os.path.abspath(os.path.join(self.BASE_DIR, 'config'))
        config_files = get_py_files(config_directory)
        module_names = [x[:-3] for x in config_files]
        data = {}
        for i, filename in enumerate(config_files):
            full_filename = os.path.join(config_directory, filename)
            module_name = module_names[i]
            data[module_name] = {}
            with open(full_filename) as f:
                text = f.read()
                code = compile(text, filename, 'exec')
                exec(code, data[module_name])
            del(data[module_name]["__builtins__"])
        self.config = namedtuple('Configuration', data.keys())(*data.values())

    def __prepare_logger(self):
        self.logger = logging.getLogger('app')

        log_level = self.config.log.get("LOG_LEVEL") or self.DEFAULT_LOG_LEVEL
        log_level = log_level.upper()
        log_level = getattr(logging, log_level)

        if "LOG_FILE" in self.config.log:
            from logging.handlers import WatchedFileHandler
            handler = WatchedFileHandler(self.config.log["LOG_FILE"])
            self.logger.addHandler(handler)
        if self.config.log.get("DEBUG"):
            handler = logging.StreamHandler(stream=sys.stdout)
            log_level = logging.DEBUG
            self.logger.addHandler(handler)

        log_format = self.config.log.get("LOG_FORMAT") or self.DEFAULT_LOG_FORMAT
        log_format = logging.Formatter(log_format)

        self.logger.setLevel(log_level)
        for handler in self.logger.handlers:
            handler.setLevel(log_level)
            handler.setFormatter(log_format)

    # shortcut method
    def run(self, **kwargs):
        self.flask.run(**kwargs)
