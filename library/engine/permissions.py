from flask import g


def current_user_is_system():
    user = get_user_from_app_context()
    if user is None:
        return False
    return user.system


def get_user_from_app_context():
    user = None
    try:
        user = g.user
    except AttributeError:
        pass
    return user


def can_create_hosts():
    user = get_user_from_app_context()
    if user is None:
        return False
    # all non-system users can create hosts. system users can only if
    # they are supervisors
    return not user.system or user.supervisor
