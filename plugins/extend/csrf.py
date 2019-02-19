from flask import request, session
from library.engine.utils import json_response


def main(app):
    if 'CSRF_PROTECTION' in app.config.app and app.config.app['CSRF_PROTECTION']:
        app.logger.debug("csrf protection plugin initializing")
        # CSRF Protection
        @app.flask.before_request
        def csrf_protect():
            if request.method != "GET":
                token = session.get('_csrf_token', None)
                if not token or token != request.form.get('_csrf_token'):
                    return json_response({'errors': ['request is not authorized: csrf token is invalid']}, 403)
    else:
        app.logger.debug("csrf protection plugin is disabled")
