import json

from automon.log import logging

from .config import OpenTelemetryConfig

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class OpenTelemetryClient(object):

    def __init__(self):
        self.config = OpenTelemetryConfig()

    async def clear(self):
        return await self.config.clear()

    async def is_ready(self):
        if await self.config.is_ready():
            return True

    async def get_finished_spans(self):
        return await self.config.get_finished_spans()

    async def to_dict(self):
        for span in await self.get_finished_spans():
            yield json.loads(span.to_json())
