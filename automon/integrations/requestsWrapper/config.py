import requests

from automon.log import logger

log = logger.logging.getLogger(__name__)
log.setLevel(logger.INFO)


class RequestsConfig(object):

    def __init__(self):
        pass

    def is_ready(self):
        return f'{NotImplemented}'

    def __repr__(self):
        return f'{NotImplemented}'
