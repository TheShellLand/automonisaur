import asyncio

from automon.log import Logging, logging

logging.getLogger("asyncioWrapper").setLevel(Logging.ERROR)


def get_event_loop():
    return asyncio.get_event_loop()
