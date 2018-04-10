from library.engine.utils import json_response
from traceback import format_exc


class ApiError(Exception):
    status_code = 400

    def __init__(self, errors, status_code=None, payload=None):
        Exception.__init__(self)
        if type(errors) != list:
            self.errors = [errors]
        else:
            self.errors = errors

        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        data = {
            "errors": self.errors,
            "error_type": self.__class__.__name__
        }
        if self.payload:
            data["data"] = self.payload
        return data

    def __repr__(self):
        return "%s: %s, status_code=%s" % (self.__class__.__name__, ", ".join(self.errors), self.status_code)

    def __str__(self):
        return "%s, status_code=%s" % (", ".join(self.errors), self.status_code)


class NotFound(ApiError):
    status_code = 404


class Conflict(ApiError):
    status_code = 409


class IntegrityError(Conflict):
    pass


class DatacenterNotFound(NotFound):
    pass


class DatacenterNotEmpty(IntegrityError):
    pass


class ParentAlreadyExists(Conflict):
    pass


class ParentCycle(IntegrityError):
    pass


class ParentDoesNotExist(NotFound):
    pass


class ChildAlreadyExists(Conflict):
    pass


class ChildDoesNotExist(NotFound):
    pass


class ObjectSaveRequired(ApiError):
    pass


class FieldRequired(ApiError):
    pass


class InvalidTags(IntegrityError):
    pass


class InvalidCustomFields(IntegrityError):
    pass


class InvalidAliases(IntegrityError):
    pass


class GroupNotFound(NotFound):
    pass


class GroupNotEmpty(IntegrityError):
    pass


class HostNotFound(NotFound):
    pass


class ProjectNotFound(NotFound):
    pass


class ProjectNotEmpty(IntegrityError):
    pass


class UserNotFound(NotFound):
    pass


class UserAlreadyExists(Conflict):
    pass


class InvalidProjectId(ApiError):
    pass


class AuthenticationError(ApiError):
    status_code = 403


class Forbidden(ApiError):
    status_code = 403


def handle_api_error(error):
    return json_response(error.to_dict(), error.status_code)


def handle_other_errors(error):
    from app import app
    app.logger.error(format_exc(error))
    return json_response({ "errors": [str(error)] }, 400)
