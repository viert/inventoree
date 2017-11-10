import os
import os.path
import sys
import importlib
import logging
import time
from flask import Flask, request, session
from datetime import timedelta
from collections import namedtuple
from library.engine.utils import get_py_files
from library.engine.json_encoder import MongoJSONEncoder
from library.mongo_session import MongoSessionInterface
from werkzeug.contrib.cache import MemcachedCache, SimpleCache
from prometheus_client import Histogram, Counter, start_http_server

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

    FLASK_REQ_LATENCY = Histogram(
        'flask_request_latency_seconds',
        'Flask Request Latency',
        ['method', 'endpoint']
    )

    FLASK_REQ_COUNT = Counter(
        'flask_request_count',
        'Flask Request Count',
        ['method', 'endpoint', 'http_status']
    )

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
        self.__prepare_logger()
        self.__prepare_flask()
        self.__set_session_expiration()
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

    def __set_session_expiration(self):
        e_time = self.config.app.get("SESSION_EXPIRATION_TIME", DEFAULT_SESSION_EXPIRATION_TIME)
        @self.flask.before_request
        def session_expiration():
            session.permanent = True
            self.flask.permanent_session_lifetime = timedelta(seconds=e_time)

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

        if "MONITOR_PORT" in self.config.app:
            self.logger.debug("Configuring prometheus exporter")

            def before_request():
                request.start_time = time.time()

            def after_request(response):
                latency = time.time() - request.start_time
                self.FLASK_REQ_LATENCY.labels(request.method, request.path).observe(latency)
                self.FLASK_REQ_COUNT.labels(request.method, request.path, response.status_code).inc()
                return response

            monitoring_port = self.config.app.get("MONITOR_PORT")
            monitoring_host = self.config.app.get("MONITOR_HOST", '')

            start_http_server(monitoring_port, monitoring_host)

            self.flask.before_request(before_request)
            self.flask.after_request(after_request)

        self.logger.debug("Setting JSON Encoder")
        self.flask.json_encoder = MongoJSONEncoder
        self.logger.debug("Setting sessions interface")
        self.flask.session_interface = MongoSessionInterface(collection_name='sessions')
        self.configure_routes()

    def configure_routes(self):
        self.logger.info("Configuring routes...")
        for route in self.config.http["ROUTES"]:
            route["active"] = True
            if not "controller" in route:
                route["active"] = False
                route["error"] = "Invalid route %s: no controller found" % route
                self.logger.error("Invalid route %s: no controller found" % route)
                continue
            if not "prefix" in route:
                route["active"] = False
                route["error"] = "Invalid route %s: no prefix found" % route
                self.logger.error("Invalid route %s: no prefix found" % route)
                continue

            module_name = "%s.%s" % (self.CTRL_MODULES_PREFIX, route["controller"])
            blueprint_name = route["controller"].split(".")[-1] + "_ctrl"
            self.logger.info("Loading controller '%s' from module %s" % (blueprint_name, module_name))
            try:
                module = importlib.import_module(module_name)
            except ImportError as e:
                route["active"] = False
                route["error"] = "Error loading controller module %s: %s" % (module_name, e)
                self.logger.error("Error loading controller module %s: %s" % (module_name, e))
                continue
            try:
                blueprint = getattr(module, blueprint_name)
            except AttributeError:
                route["active"] = False
                route["error"] = "No blueprint named %s found in module %s" % (blueprint_name, module_name)
                self.logger.error("No blueprint named %s found in module %s" % (blueprint_name, module_name))
                continue
            self.flask.register_blueprint(blueprint, url_prefix=route["prefix"])
            self.logger.info("Registered blueprint '%s' with url_prefix=%s" % (blueprint_name, route["prefix"]))

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

    # shortcut method
    def run(self, **kwargs):
        self.flask.run(**kwargs)
