import errno
import os
import re
from collections.abc import Callable
from functools import cache

from veilid.json_api import _JsonVeilidAPI

import veilid

ERRNO_PATTERN = re.compile(r"errno (\d+)", re.IGNORECASE)


class VeilidTestConnectionError(Exception):
    """The test client could not connect to the veilid-server."""

    pass


@cache
def server_info() -> tuple[str, int]:
    """Return the hostname and port of the test server."""
    VEILID_SERVER = os.getenv("VEILID_SERVER")
    if VEILID_SERVER is None:
        return "localhost", 5959

    hostname, *rest = VEILID_SERVER.split(":")
    if rest:
        return hostname, int(rest[0])
    return hostname, 5959


async def api_connector(callback: Callable) -> _JsonVeilidAPI:
    """Return an API connection if possible.

    If the connection fails due to an inability to connect to the
    server's socket, raise an easy-to-catch VeilidTestConnectionError.
    """

    hostname, port = server_info()
    try:
        return await veilid.json_api_connect(hostname, port, callback)
    except OSError as exc:
        # This is a little goofy. The underlying Python library handles
        # connection errors in 2 ways, depending on how many connections
        # it attempted to make:
        #
        # - If it only tried to connect to one IP address socket, the
        # library propagates the one single OSError it got.
        #
        # - If it tried to connect to multiple sockets, perhaps because
        # the hostname resolved to several addresses (e.g. "localhost"
        # => 127.0.0.1 and ::1), then the library raises one exception
        # with all the failure exception strings joined together.

        # If errno is set, it's the first kind of exception. Check that
        # it's the code we expected.
        if exc.errno is not None:
            if exc.errno == errno.ECONNREFUSED:
                raise VeilidTestConnectionError
            raise

        # If not, use a regular expression to find all the errno values
        # in the combined error string. Check that all of them have the
        # code we're looking for.
        errnos = ERRNO_PATTERN.findall(str(exc))
        if all(int(err) == errno.ECONNREFUSED for err in errnos):
            raise VeilidTestConnectionError

        raise
