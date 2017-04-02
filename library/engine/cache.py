import functools
from datetime import datetime

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
            value = app.cache.get(cache_key)
            if value is None:
                value = func(*args, **kwargs)
                if value is not None:
                    # caching only positive if positive_only
                    if not positive_only or value:
                        app.cache.set(cache_key, value, timeout=cache_timeout)
                app.logger.debug("Cache MISS %s (%.3f seconds)" % (cached_call, (datetime.now() - t1).total_seconds() ))
            else:
                app.logger.debug("Cache HIT %s (%.3f seconds)" % (cached_call, (datetime.now() - t1).total_seconds() ))
            return value
        return wrapper
    return cache_decorator