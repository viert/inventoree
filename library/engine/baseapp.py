import os
import os.path
import sys
import importlib
import logging
import time
from flask import Flask, request, session
from datetime import timedelta
from collections import namedtuple
from library.engine.utils import get_py_files, uuid4_string
from library.engine.errors import ApiError, handle_api_error, handle_other_errors
from library.engine.json_encoder import MongoJSONEncoder
from library.mongo_session import MongoSessionInterface
from werkzeug.contrib.cache import MemcachedCache, SimpleCache

ENVIRONMENT_TYPES = (
    "development",
    "testing",
    "production",
)

DEFAULT_ENVIRONMENT_TYPE = "development"
DEFAULT_SESSION_EXPIRATION_TIME = 86400 * 7 * 2 # 2 weeks


class BaseApp(object):

    DEFAULT_LOG_FORMAT = "[%(asctime)s] %(levelname)s %(filename)s:%(lineno)d %(message)s"
    DEFAULT_LOG_LEVEL = "debug"
    CTRL_MODULES_PREFIX = "app.controllers"

    def __init__(self):
        import inspect
        class_file = inspect.getfile(self.__class__)
        self.APP_DIR = os.path.dirname(os.path.abspath(class_file))
        self.BASE_DIR = os.path.abspath(os.path.join(self.APP_DIR, "../"))
        # detecting environment type
        self.envtype = os.environ.get("CONDUCTOR_ENV")
        if not self.envtype in ENVIRONMENT_TYPES:
            self.envtype = DEFAULT_ENVIRONMENT_TYPE
        self.__read_config()
        self.test_config()
        self.after_configured()
        self.__prepare_logger()
        self.__load_plugins()
        self.__prepare_flask()
        self.__set_authorizer()
        self.__set_session_expiration()
        self.__set_request_id()
        self.__set_request_times()
        self.__set_cache()

    def __set_cache(self):
        self.logger.debug("Setting up the cache")
        if hasattr(self.config, 'cache') and "MEMCACHE_BACKENDS" in self.config.cache:
            self.cache = MemcachedCache(self.config.cache["MEMCACHE_BACKENDS"])
        else:
            self.cache = SimpleCache()

    def __load_plugins(self):
        self.plugins = []
        plugin_directory = os.path.abspath(os.path.join(self.BASE_DIR, 'plugins'))
        plugin_files = get_py_files(plugin_directory)
        module_names = [x[:-3] for x in plugin_files if not x.startswith("__")]
        for module_name in module_names:
            try:
                self.logger.debug("Loading plugin %s" % module_name)
                module = importlib.import_module("plugins.%s" % module_name)
            except ImportError as e:
                self.logger.error("Error loading module %s: %s" % (module_name, e.message))
            self.plugins.append(module)

    def __set_authorizer(self):
        authorizer_name = self.config.app.get("AUTHORIZER", "LocalAuthorizer")
        self.authorizer = None
        authorizer_class = None
        for plugin in self.plugins:
            try:
                authorizer_class = getattr(plugin, authorizer_name)
            except AttributeError:
                continue
        if authorizer_class is None:
            raise RuntimeError("No authorizer '%s' found in plugins" % authorizer_name)
        else:
            self.authorizer = authorizer_class(self.flask)
            self.logger.debug("Authorizer '%s' registered" % authorizer_name)

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

    def __set_session_expiration(self):
        e_time = self.config.app.get("SESSION_EXPIRATION_TIME", DEFAULT_SESSION_EXPIRATION_TIME)
        @self.flask.before_request
        def session_expiration():
            session.permanent = True
            self.flask.permanent_session_lifetime = timedelta(seconds=e_time)

    def __set_request_id(self):
        @self.flask.before_request
        def add_request_id():
            if not hasattr(request, "id"):
                setattr(request, "id", uuid4_string())

    def __set_request_times(self):
        @self.flask.before_request
        def add_request_started_time():
            setattr(request, "started", time.time())

        @self.flask.after_request
        def add_request_time_logging(response):
            dt = time.time() - request.started
            self.logger.debug("%s completed in %.3fs" % (request.full_path, dt))
            return response

    def __prepare_flask(self):
        self.logger.debug("Creating flask app")
        static_folder = self.config.app.get("STATIC", "static")
        flask_app_settings = self.config.app.get("FLASK_APP_SETTINGS", {})
        static_folder = os.path.abspath(os.path.join(self.BASE_DIR, static_folder))
        self.flask = Flask(__name__, static_folder=static_folder)

        self.logger.debug("Applying Flask application settings")
        for k, v in flask_app_settings.items():
            self.logger.debug("  %s: %s" % (k, v))
            self.flask.config[k] = v

        self.logger.debug("Setting JSON Encoder")
        self.flask.json_encoder = MongoJSONEncoder
        self.logger.debug("Setting sessions interface")
        self.flask.session_interface = MongoSessionInterface(collection_name='sessions')
        self.flask._register_error_handler(None, ApiError, handle_api_error)
        self.flask._register_error_handler(None, Exception, handle_other_errors)
        self.configure_routes()

    def configure_routes(self):
        pass

    def __read_config(self):
        # reading and compiling config files
        config_directory = os.path.abspath(os.path.join(self.BASE_DIR, 'config', self.envtype))
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
        self.logger.propagate = False

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
        self.logger.info("Logger created. Environment type set to %s" % self.envtype)

    def test_config(self):
        pass

    def after_configured(self):
        pass

    # shortcut method
    def run(self, **kwargs):
        self.flask.run(**kwargs)
