import functools
import json
import copy
from library.engine.errors import ApiError, handle_other_errors, handle_api_error

action_types = []


def logged_action(action_type):
    global action_types
    action_types.append(action_type)
    action_types.sort()

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

            action.status = "error"
            try:
                response = func(*args, **kwargs)
                if 100 <= response.status_code < 300:
                    action.status = "success"
                else:
                    app.logger.error("Action status set to error, response.data is following")
                    try:
                        data = json.loads(response.data)
                        if "errors" in data:
                            action.errors = data["errors"]
                    except:
                        pass
            except ApiError as ae:
                app.logger.error("Catched ApiError")
                action.status = "error"
                response = handle_api_error(ae)
                data = json.loads(response.data)
                action.errors = data["errors"]
                app.logger.debug("action '%s' status updated to %s" % (action.action_type, action.status))
                action.save()
                raise
            except Exception as e:
                app.logger.error("Catched Exception")
                action.status = "error"
                response = handle_other_errors(e)
                data = json.loads(response.data)
                action.errors = data["errors"]
                app.logger.debug("action '%s' status updated to %s" % (action.action_type, action.status))
                action.save()
                raise
            app.logger.debug("action '%s' status updated to %s" % (action.action_type, action.status))
            action.save()
            return response
        return wrapper
    return log_action_decorator
