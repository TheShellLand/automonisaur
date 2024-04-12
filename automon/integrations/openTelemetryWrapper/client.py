import json

from opentelemetry.util import types
from opentelemetry.trace import Status, StatusCode

from automon.log import logging

from .config import OpenTelemetryConfig

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class OpenTelemetryClient(object):

    def __init__(self):
        self.config = OpenTelemetryConfig()

    async def add_event(self, name: str, attributes: types.Attributes = None, **kwargs):
        logger.debug(dict(name=name, attributes=attributes, kwargs=kwargs))
        span = await self.current_span()
        return span.add_event(name=name, attributes=attributes, **kwargs)

    async def clear(self):
        logger.debug('clear')
        return await self.config.clear()

    async def current_span(self):
        logger.debug('current_span')
        return await self.config.current_span()

    async def is_ready(self):
        if await self.config.is_ready():
            return True

    async def get_finished_spans(self):
        logger.debug('get_finished_spans')
        return await self.config.get_finished_spans()

    async def pop_finished_spans(self):
        logger.debug('pop_finished_spans')
        return await self.config.pop_finished_spans()

    async def record_exception(self, exception: Exception):
        logger.error(f'{exception}')
        span = await self.current_span()
        span.set_status(Status(StatusCode.ERROR))
        return span.record_exception(exception=exception)

    async def start_as_current_span(
            self, name: str,
            attributes: types.Attributes = None,
            **kwargs
    ):
        logger.debug(dict(name=name, attributes=attributes, kwargs=kwargs))
        return self.config.tracer.start_as_current_span(
            name=name,
            attributes=attributes,
            **kwargs)

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

    async def test(self):
        with await self.start_as_current_span(name='rootSpan') as trace_root:
            await self.add_event('AAAAAAAA')

            with await self.start_as_current_span(name='childSpan') as trace_child:
                await self.add_event('AAAAAAAA')
                await self.add_event('BBBBBBBB')

            await self.add_event('BBBBBBBB')

        return True

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

            log.append(dict(
                ddsource=ddsource,
                ddtags=ddtags,
                hostname=hostname,
                service=service,
                message=message,
            ))
        return log
