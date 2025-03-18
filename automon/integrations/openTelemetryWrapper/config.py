import opentelemetry
import queue

import opentelemetry.sdk.trace
import opentelemetry.sdk.trace.export
import opentelemetry.sdk.trace.export.in_memory_span_exporter
import opentelemetry.exporter.otlp.proto.grpc.trace_exporter

from automon.helpers.osWrapper import environ
from automon.helpers.loggingWrapper import LoggingClient, DEBUG, INFO

logger = LoggingClient.logging.getLogger(__name__)
logger.setLevel(DEBUG)


class OpenTelemetryConfig(object):
    def __init__(self, endpoint: str = None, insecure: bool = False):
        self.endpoint = endpoint or environ('OTEL_EXPORTER_OTLP_TRACES_ENDPOINT')
        self.insecure = insecure or environ('OTEL_EXPORTER_OTLP_TRACES_ENDPOINT_INSECURE')

        self.opentelemetry = opentelemetry
        self.provider = opentelemetry.sdk.trace.TracerProvider()

        self.tracer = None

        self.queue_consumer = queue.Queue()
        self.queue_producer = queue.Queue()

    def enable_memory_processor(self):
        """Enable simple in-memory exporter"""
        exporter = opentelemetry.sdk.trace.export.in_memory_span_exporter.InMemorySpanExporter()
        span_processor = opentelemetry.sdk.trace.export.SimpleSpanProcessor(exporter)

        self.provider.add_span_processor(span_processor)
        opentelemetry.trace.set_tracer_provider(self.provider)

        self.tracer = opentelemetry.trace.get_tracer(__name__)
        logger.info(f"enable_memory_processor :: done")
        return self

    def enable_batch_processor(self):
        """Enable external endpoint exporter"""
        exporter = opentelemetry.exporter.otlp.proto.grpc.trace_exporter.OTLPSpanExporter(endpoint=self.endpoint,
                                                                                          insecure=self.insecure)
        span_processor = opentelemetry.sdk.trace.export.BatchSpanProcessor(exporter)

        self.provider.add_span_processor(span_processor)
        opentelemetry.trace.set_tracer_provider(self.provider)

        self.tracer = opentelemetry.trace.get_tracer(__name__)
        logger.info(f"enable_batch_processor :: done")
        return self

    # def clear(self):
    #     logger.debug('clear')
    #     return self.memory_processor.clear()

    @property
    def get_current_span(self):
        return opentelemetry.trace.get_current_span()

    def is_ready(self):
        if self.tracer:
            return True
        logger.error(f"No tracers enabled")
        return False

    # def get_finished_spans(self):
    #     logger.debug('get_finished_spans')
    #     return self.memory_processor.get_finished_spans()

    # def pop_finished_spans(self):
    #     """ideal is to lock, pop spans, and clear"""
    #     spans = self.get_finished_spans()
    #     clear = self.clear()
    #     return spans

    def test(self):
        with self.tracer.start_as_current_span(name="rootSpan") as trace_root:
            trace_root.add_event('AAAAAAAA')
            with self.tracer.start_as_current_span(name="childSpan") as trace_child:
                trace_child.add_event('AAAAAAAA')
                trace_child.add_event('BBBBBBBB')

        return True
