import functools
import json
import copy

def logged_action(action_type):
    def log_action_decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            from app import app
            if not app.action_logging:
                return func(*args, **kwargs)

            from app.models import ApiAction
            from flask import g, request
            if g.user is None:
                username = "_unauthorized_"
            else:
                username = g.user.username
            if request.json is not None:
                action_args = copy.deepcopy(request.json)
            else:
                action_args = {}

            arg_keys = action_args.keys()
            # removing plain text passwords from action log
            for k in arg_keys:
                if k.startswith("password"):
                    del(action_args[k])

            action = ApiAction(
                username=username,
                action_type=action_type,
                kwargs=kwargs,
                params=action_args,
                status="requested"
            )
            action.save()
            app.logger.debug("action '%s' created" % action.action_type)
            response = func(*args, **kwargs)
            if response.status_code == 200:
                action.status="success"
            else:
                action.status="error"
                try:
                    data = json.loads(response.data)
                    if "errors" in data:
                        action.errors = data["errors"]
                except:
                    pass
            app.logger.debug("action '%s' status updated to %s" % (action.action_type, action.status))
            action.save()
            return response
        return wrapper
    return log_action_decorator