import requests

from automon import log

logger = log.logging.getLogger(__name__)
logger.setLevel(log.INFO)


class RequestsConfig(object):

    def __init__(self):
        pass

    def is_ready(self):
        return f'{NotImplemented}'

    def __repr__(self):
        return f'{NotImplemented}'
