import functools
from datetime import datetime
from flask import request, g

DEFAULT_CACHE_PREFIX = 'microeng'
DEFAULT_CACHE_TIMEOUT = 3600


def _get_cache_key(pref, funcname, args, kwargs):
    from hashlib import md5
    key = "%s:%s(%s.%s)" % (pref, funcname, md5(str(args)).hexdigest(), md5(str(kwargs)).hexdigest())
    kwargs_str = ", ".join(["%s=%s" % (x[0], x[1]) for x in kwargs.items()])
    arguments = ""
    if len(args) > 0:
        arguments = ", ".join([str(x) for x in args])
        if len(kwargs) > 0:
            arguments += ", " + kwargs_str
    else:
        if len(kwargs) > 0:
            arguments = kwargs
    cached_call = "%s:%s(%s)" % (pref, funcname, arguments)
    return key, cached_call


def cached_function(cache_key_prefix=DEFAULT_CACHE_PREFIX, cache_timeout=DEFAULT_CACHE_TIMEOUT, positive_only=False):
    def cache_decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            from app import app
            cache_key, cached_call = _get_cache_key(cache_key_prefix, func.__name__, args, kwargs)
            t1 = datetime.now()

            if app.cache.has(cache_key):
                value = app.cache.get(cache_key)
                app.logger.debug("Cache HIT %s (%.3f seconds)" % (cached_call, (datetime.now() - t1).total_seconds()))
            else:
                value = func(*args, **kwargs)
                if value or not positive_only:
                    app.cache.set(cache_key, value, timeout=cache_timeout)
                app.logger.debug("Cache MISS %s (%.3f seconds)" % (cached_call, (datetime.now() - t1).total_seconds()))
            return value
        return wrapper
    return cache_decorator


def check_cache():
    from app import app
    from hashlib import md5
    from random import randint
    k = md5(str(randint(0, 1000000))).hexdigest()
    v = md5(str(randint(0, 1000000))).hexdigest()
    app.cache.set(k, v)
    if app.cache.get(k) != v:
        return False
    else:
        app.cache.delete(k)
        return True


def request_time_cache(cache_key_prefix=DEFAULT_CACHE_PREFIX):
    """
    Decorator used for caching data during one api request.
    It's useful while some "list something" handlers with a number of cross-references generate
    many repeating database requests which are known to generate the same response during the api request.
    I.e. list of 20 hosts included in the same group and inheriting the same set of tags/custom fields
    may produce 20 additional db requests and 20 requests for each parent group recursively. This may be fixed
    by caching db responses in flask "g" store.
    """
    def cache_decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            from app import app
            from library.db import ObjectsCursor
            try:
                request_id = request.id
            except (RuntimeError, AttributeError):
                # cache only if request id is available
                return func(*args, **kwargs)
            cache_key, cached_call = _get_cache_key(cache_key_prefix, func.__name__, args, kwargs)
            t1 = datetime.now()

            if not hasattr(g, "_request_local_cache"):
                g._request_local_cache = {}

            if cache_key not in g._request_local_cache:
                value = func(*args, **kwargs)
                g._request_local_cache[cache_key] = value
                ts = (datetime.now() - t1).total_seconds()
                app.logger.debug("RequestTimeCache %s MISS %s (%.3f seconds)" % (request_id, cache_key, ts))
            else:
                value = g._request_local_cache[cache_key]
                if type(value) == ObjectsCursor:
                    value.cursor.rewind()
                ts = (datetime.now() - t1).total_seconds()
                app.logger.debug("RequestTimeCache %s HIT %s (%.3f seconds)" % (request_id, cache_key, ts))
            return value
        return wrapper
    return cache_decorator


def _get_custom_data_cache_key(obj):
    from app import app
    try:
        model = type(obj).__name__
        model_id = obj._id
        return "%s.%s.custom_data" % (model, model_id)
    except Exception as e:
        app.logger.error("error generating custom_data cache key: %s" % e)
        return None


def cache_custom_data(func):
    """
    cache_custom_data decorator is used to cache merged custom_data _forever_.
    invalidating custom data cache should be done using recursive calls to invalidate_custom_data(obj)
    """
    from app import app

    @functools.wraps(func)
    def wrapper(self):
        cache_key = _get_custom_data_cache_key(self)
        if cache_key is None:
            return func(self)

        t1 = datetime.now()
        if app.cache.has(cache_key):
            value = app.cache.get(cache_key)
            app.logger.debug("%s HIT (%.3f seconds)" % (cache_key, (datetime.now() - t1).total_seconds()))
        else:
            value = func(self)
            app.cache.set(cache_key, value)
            app.logger.debug("%s MISS (%.3f seconds)" % (cache_key, (datetime.now() - t1).total_seconds()))
        return value

    return wrapper


def invalidate_custom_data(obj):
    from app import app
    cache_key = _get_custom_data_cache_key(obj)
    if app.cache.has(cache_key):
        app.cache.delete(cache_key)
        app.logger.debug("%s DELETE cache" % cache_key)
    else:
        app.logger.debug("%s MIGHT DELETE cache" % cache_key)
