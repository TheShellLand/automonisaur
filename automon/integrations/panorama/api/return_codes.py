class PanoramaBaseException(Exception):
    pass


class BadRequest(PanoramaBaseException):
    """400
    Bad request
    A required parameter is missing, an illegal parameter value is used.
    """
    pass


class Forbidden(PanoramaBaseException):
    """403
    Forbidden
    Authentication or authorization errors including invalid key or insufficient admin access rights. Learn how to Get Your API Key
    """
    pass


class UnknownCommand(PanoramaBaseException):
    """1
    Unknown command
    The specific config or operational command is not recognized.
    """
    pass


class InternalErrors(PanoramaBaseException):
    """2-5
    Internal errors
    Check with technical support when seeing these errors.
    """
    pass


class BadXpath(PanoramaBaseException):
    """6
    Bad Xpath
    The xpath specified in one or more attributes of the command is invalid. Check the API browser for proper xpath values.
    """
    pass


class ObjectNotPresent(PanoramaBaseException):
    """7
    Object not present
    Object specified by the xpath is not present. For example, entry[@name='value'] where no object with name 'value' is present.
    """
    pass


class ObjectNotUnique(PanoramaBaseException):
    """8
    Object not unique
    For commands that operate on a single object, the specified object is not unique.
    """
    pass


class ReferenceCountNotZero(PanoramaBaseException):
    """10
    Reference count not zero
    Object cannot be deleted as there are other objects that refer to it. For example, address object still in use in policy.
    """
    pass


class InternalError11(PanoramaBaseException):
    """11
    Internal error
    Check with technical support when seeing these errors.
    """
    pass


class InvalidObject(PanoramaBaseException):
    """12
    Invalid object
    Xpath or element values provided are not complete.
    """
    pass


class ObjectNotFound(PanoramaBaseException):
    """13
    Object not found
    Object presented in the request could not be found.
    """
    pass


class OperationNotPossible(PanoramaBaseException):
    """14
    Operation not possible
    Operation is allowed but not possible in this case. For example, moving a rule up one position when it is already at the top.
    """
    pass


class OperationDenied(PanoramaBaseException):
    """15
    Operation denied
    Operation is allowed. For example, Admin not allowed to delete own account, Running a command that is not allowed on a passive device.
    """
    pass


class Unauthorized(PanoramaBaseException):
    """16
    Unauthorized
    The API role does not have access rights to run this query.
    """
    pass


class OperationDenied(PanoramaBaseException):
    """15
    Operation denied
    Operation is allowed. For example, Admin not allowed to delete own account, Running a command that is not allowed on a passive device.
    """
    pass


class Unauthorized(PanoramaBaseException):
    """16
    Unauthorized
    The API role does not have access rights to run this query.
    """
    pass


class InvalidCommand(PanoramaBaseException):
    """17
    Invalid command
    Invalid command or parameters.
    """
    pass


class MalformedCommand(PanoramaBaseException):
    """18
    Malformed command
    The XML is malformed.
    """
    pass


class Success:
    """19-20
    Success
    Command completed successfully.
    """
    pass


class InternalError21(PanoramaBaseException):
    """21
    Internal error
    Check with technical support when seeing these errors.
    """
    pass


class SessionTimedOut(PanoramaBaseException):
    """22
    Session timed out
    The session for this query timed out.
    """
    pass
