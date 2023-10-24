import asyncio

from automon.log import logger

log = logger.logging.getLogger(__name__)
log.setLevel(logger.DEBUG)


def get_event_loop():
    return asyncio.get_event_loop()
