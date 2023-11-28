import inspect
from dataclasses import dataclass
from typing import Any, Self

_ERROR_REGISTRY: dict[str, type] = {}


class VeilidAPIError(Exception):
    """Veilid API error exception base class"""

    label = "Base class"

    def __init__(self, *args, **kwargs):
        super().__init__(self.label, *args, **kwargs)

    def __str__(self) -> str:
        args = [('label', self.label)] + sorted(vars(self).items())
        return " ".join(f"{key}={value!r}" for (key, value) in args)

    @classmethod
    def from_json(cls, json: dict) -> Self:
        kind = json["kind"]
        try:
            error_class = _ERROR_REGISTRY[kind]
        except KeyError:
            return cls(f"Unknown exception type: {kind}")

        args = {key: value for key, value in json.items() if key != "kind"}
        return error_class(**args)


@dataclass
class VeilidAPIErrorNotInitialized(VeilidAPIError):
    """Veilid was not initialized"""

    label = "Not initialized"


@dataclass
class VeilidAPIErrorAlreadyInitialized(VeilidAPIError):
    """Veilid was already initialized"""

    label = "Already initialized"


@dataclass
class VeilidAPIErrorTimeout(VeilidAPIError):
    """Veilid operation timed out"""

    label = "Timeout"


@dataclass
class VeilidAPIErrorTryAgain(VeilidAPIError):
    """Operation could not be performed at this time, retry again later"""

    label = "Try again"
    message: str


@dataclass
class VeilidAPIErrorShutdown(VeilidAPIError):
    """Veilid was already shut down"""

    label = "Shutdown"


@dataclass
class VeilidAPIErrorInvalidTarget(VeilidAPIError):
    """Target of operation is not valid"""

    label = "Invalid target"
    message: str


@dataclass
class VeilidAPIErrorNoConnection(VeilidAPIError):
    """Connection could not be established"""

    label = "No connection"
    message: str


@dataclass
class VeilidAPIErrorKeyNotFound(VeilidAPIError):
    """Key was not found"""

    label = "Key not found"
    key: str


@dataclass
class VeilidAPIErrorInternal(VeilidAPIError):
    """Veilid experienced an internal failure"""

    label = "Internal"
    message: str


@dataclass
class VeilidAPIErrorUnimplemented(VeilidAPIError):
    """Functionality is not yet implemented"""

    label = "Unimplemented"
    message: str


@dataclass
class VeilidAPIErrorParseError(VeilidAPIError):
    """Value was not in a parseable format"""

    label = "Parse error"
    message: str
    value: str


@dataclass
class VeilidAPIErrorInvalidArgument(VeilidAPIError):
    """Argument is not valid in this context"""

    label = "Invalid argument"
    context: str
    argument: str
    value: str


@dataclass
class VeilidAPIErrorMissingArgument(VeilidAPIError):
    """Required argument was missing"""

    label = "Missing argument"
    context: str
    argument: str


@dataclass
class VeilidAPIErrorGeneric(VeilidAPIError):
    """Generic error message"""

    label = "Generic"
    message: str


# Build a mapping of canonicalized labels to their exception classes. Do this in-place to update
# the object inside the closure so VeilidAPIError.from_json can access the values.
_ERROR_REGISTRY.clear()
_ERROR_REGISTRY.update(
    {
        obj.label.title().replace(" ", ""): obj
        for obj in vars().values()
        if inspect.isclass(obj) and issubclass(obj, VeilidAPIError)
    }
)


def raise_api_result(api_result: dict) -> Any:
    if "value" in api_result:
        return api_result["value"]
    if "error" in api_result:
        raise VeilidAPIError.from_json(api_result["error"])
    raise ValueError("Invalid format for ApiResult")
