import requests

from automon.log import Logging

log = Logging(name='RequestsConfig', level=Logging.DEBUG)


class RequestsConfig(object):

    def __init__(self):
        pass

    def isReady(self):
        return f'{NotImplemented}'

    def __repr__(self):
        return f'{NotImplemented}'
