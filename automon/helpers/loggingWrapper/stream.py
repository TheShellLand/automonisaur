from .client import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.CRITICAL)


class LoggingStream(object):
    """Allows logging to string
    """

    def __init__(self):
        self.logs = ''

    def write(self, string):
        self.logs += string

    def flush(self):
        pass

    def __repr__(self):
        return self.logs
