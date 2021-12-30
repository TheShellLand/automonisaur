import requests

from automon import Logging


class RequestsConfig(object):
    def __init__(self):
        self._log = Logging(name=RequestsConfig.__name__, level=Logging.DEBUG)
