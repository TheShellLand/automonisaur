from .client import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.CRITICAL)


class LoggingHandler(object):
    pass
