from flask import Flask
from automon.log import Logging
from automon.serverless import Requests

log = Logging(__name__, level=Logging.DEBUG)


def request_json(requests: Flask) -> bytes:
    r = Requests(requests)
    log.debug(r)
    return r.toJson()
