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

    async def start_consumer(self):
        """adds spans from memory to queue"""
        while True:
            pass
        return

    async def start_producer(self):
        """"""
        while True:
            pass
        return

    async def to_dict(self):
        return [
            json.loads(span.to_json())
            for span in await self.get_finished_spans()
        ]

    async def to_datadog(self):
        log = []
        for span in await self.to_dict():
            message = dict(span).copy()
            ddsource = None
            ddtags = ','.join([f"{x[0]}:{x[1]}" for x in span.get("resource").get("attributes").items()])
            hostname = span['context']['trace_id']
            service = span['context']['span_id']

            span['datadog'] = dict(
                ddsource=ddsource,
                ddtags=ddtags,
                hostname=hostname,
                service=service,
                message=message,
            )
            log.append(span)
        return log
