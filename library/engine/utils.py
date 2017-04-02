from flask import make_response
import os
import flask.json as json

def json_response(data, code=200):
    from app import app
    json_kwargs = {}
    if app.config.log.get("DEBUG"):
        json_kwargs["indent"] = 4
    return make_response(json.dumps(data, **json_kwargs), code, {'Content-Type':'application/json'})


def json_exception(exception, code=400):
    data = exception.to_dict()
    errors = []
    for k,v in data.items():
        errors.append('%s %s' % (k,v))
    return make_response(json.dumps({'errors': errors}), code, {'Content-Type':'application/json'})


def get_py_files(directory):
    return [f for f in os.listdir(directory) if f.endswith(".py")]


def get_modules(directory):
    return [x[:-3] for x in get_py_files(directory) if x != "__init__.py"]