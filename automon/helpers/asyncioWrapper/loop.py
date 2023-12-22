import asyncio

from automon import log

logger = log.logging.getLogger(__name__)
logger.setLevel(log.DEBUG)


def get_event_loop():
    return asyncio.get_event_loop()
