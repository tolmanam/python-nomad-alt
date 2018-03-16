class NomadException(Exception):
    pass


class ACLDisabled(NomadException):
    pass


class ACLPermissionDenied(NomadException):
    pass


class NotFound(NomadException):
    pass


class Timeout(NomadException):
    pass


class BadRequest(NomadException):
    pass