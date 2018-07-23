from app.controllers.auth_controller import AuthController
from os.path import dirname, join
from flask import make_response

doc_ctrl = AuthController("doc", __name__, require_auth=False)


@doc_ctrl.route("/")
def doc():
    dochtml = join(dirname(__file__), 'doc.html')
    with open(dochtml) as f:
        r = make_response(f.read())
        r.headers["Content-Type"] = "text/html"
    return r
