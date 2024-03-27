import asyncio

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

from automon.log import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class OpenTelemetryConfig(object):
    def __init__(self):
        self.provider = TracerProvider()
        self.memory_processor = InMemorySpanExporter()
        self.processor = SimpleSpanProcessor(self.memory_processor)
        self.provider.add_span_processor(self.processor)

        trace.set_tracer_provider(self.provider)

        self.tracer = trace.get_tracer(__name__)

        self.queue_consumer = asyncio.Queue()
        self.queue_producer = asyncio.Queue()

    async def clear(self):
        return self.memory_processor.clear()

    async def is_ready(self):
        if self.provider and self.memory_processor and self.processor:
            return True

    async def get_finished_spans(self):
        return self.memory_processor.get_finished_spans()

    async def pop_finished_spans(self):
        """ideal is to lock, pop spans, and clear"""
        spans = await self.get_finished_spans()
        clear = await self.clear()
        return spans

    async def test(self):
        with self.tracer.start_as_current_span("rootSpan"):
            with self.tracer.start_as_current_span("childSpan"):
                print("Hello world!")

        return True
