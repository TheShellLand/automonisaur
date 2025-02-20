import asyncio

from automon.helpers.loggingWrapper import LoggingClient, DEBUG, INFO

logger = LoggingClient.logging.getLogger(__name__)
logger.setLevel(DEBUG)


def get_event_loop():
    return asyncio.get_event_loop()
