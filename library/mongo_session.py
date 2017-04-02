from uuid import uuid4
from datetime import datetime, timedelta
from flask.sessions import SessionInterface, SessionMixin
from werkzeug.datastructures import CallbackDict


class MongoSession(CallbackDict, SessionMixin):
    def __init__(self, initial=None, sid=None):
        CallbackDict.__init__(self, initial)
        self.sid = sid
        self.modified = False


class MongoSessionInterface(SessionInterface):
    def __init__(self, collection_name='sessions'):
        self.collection_name = collection_name

    def open_session(self, app, request):
        from library.db import db
        sid = request.cookies.get(app.session_cookie_name)
        if sid:
            stored_session = db.get_session(sid, collection=self.collection_name)
            if stored_session:
                if stored_session.get('expiration') > datetime.utcnow():
                    return MongoSession(initial=stored_session['data'], sid=stored_session['sid'])
        sid = str(uuid4())
        return MongoSession(sid=sid)

    def save_session(self, app, session, response):
        from library.db import db
        domain = self.get_cookie_domain(app)
        if not session:
            response.delete_cookie(app.session_cookie_name, domain=domain)
            return
        expiration = self.get_expiration_time(app, session)
        if not expiration:
            expiration = datetime.utcnow() + timedelta(hours=1)
        db.update_session(session.sid, session, expiration, collection=self.collection_name)
        response.set_cookie(app.session_cookie_name, session.sid,
                            expires=self.get_expiration_time(app, session),
                            httponly=True, domain=domain)