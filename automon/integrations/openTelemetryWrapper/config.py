import os

try:
    import opentelemetry
    import queue

    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import SimpleSpanProcessor, BatchSpanProcessor
    from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter as OTLPSpanExporterHTTP
    from opentelemetry.trace import set_tracer_provider, get_tracer
except:
    class TracerProvider:

        def add_span_processor(self, *args, **kwrags):
            pass


    class SimpleSpanProcessor:
        def __init__(self, *args, **kwargs):
            pass


    class BatchSpanProcessor:
        def __init__(self, *args, **kwrags):
            pass


    class InMemorySpanExporter:
        pass


    class OTLPSpanExporter:
        def __init__(self, *args, **kwargs):
            pass


    class OTLPSpanExporterHTTP:
        def __init__(self, *args, **kwargs):
            pass


    def set_tracer_provider(*args, **kwargs):
        pass


    def get_tracer(*args, **kwargs):
        pass

from automon.helpers.networking import Networking

from automon.helpers.osWrapper import environ, environ_set
from automon.helpers.loggingWrapper import LoggingClient, DEBUG, INFO

logger = LoggingClient.logging.getLogger(__name__)
logger.setLevel(DEBUG)


class OpenTelemetryConfig(object):
    def __init__(self,
                 endpoint: str = None,
                 endpoint_traces: str = None,
                 insecure: bool = False,
                 token: str = None
                 ):
        self.OTEL_EXPORTER_OTLP_ENDPOINT = endpoint or environ('OTEL_EXPORTER_OTLP_ENDPOINT')
        self.OTEL_EXPORTER_OTLP_TRACES_ENDPOINT = endpoint_traces or environ('OTEL_EXPORTER_OTLP_TRACES_ENDPOINT')
        self.OTEL_EXPORTER_OTLP_HEADERS = environ('OTEL_EXPORTER_OTLP_HEADERS')

        self.OTEL_EXPORTER_OTLP_TOKEN = token or environ('OTEL_EXPORTER_OTLP_TOKEN')
        self.insecure = insecure

        # header = f'Authorization={Networking.quote(f"Bearer {self.OTEL_EXPORTER_OTLP_TOKEN}")}'
        # environ_set('OTEL_EXPORTER_OTLP_HEADERS', Networking.quote(header))

        self.opentelemetry = opentelemetry
        self.provider = TracerProvider()

        self.tracer = None

        self.queue_consumer = queue.Queue()
        self.queue_producer = queue.Queue()

    @property
    def headers(self):
        if self.OTEL_EXPORTER_OTLP_TOKEN is not None:
            return {
                'Authorization': f"{Networking.quote(self.OTEL_EXPORTER_OTLP_TOKEN)}"
            }

    @property
    def endpoint(self):
        if self.OTEL_EXPORTER_OTLP_ENDPOINT:
            return self.OTEL_EXPORTER_OTLP_ENDPOINT
        if self.OTEL_EXPORTER_OTLP_TRACES_ENDPOINT:
            return self.OTEL_EXPORTER_OTLP_TRACES_ENDPOINT

    def enable_memory_processor(self):
        """Enable simple in-memory exporter"""
        exporter = InMemorySpanExporter()
        span_processor = SimpleSpanProcessor(exporter)

        self.provider.add_span_processor(span_processor)
        set_tracer_provider(self.provider)

        self.tracer = get_tracer(__name__)
        logger.info(f"enable_memory_processor :: done")
        return self

    def enable_batch_processor_grpc(self):
        """Enable external endpoint exporter"""
        exporter = OTLPSpanExporter(endpoint=self.endpoint,
                                    insecure=self.insecure,
                                    headers=self.headers
                                    )
        span_processor = BatchSpanProcessor(exporter)

        self.provider.add_span_processor(span_processor)
        opentelemetry.trace.set_tracer_provider(self.provider)

        self.tracer = get_tracer(__name__)
        logger.info(f"enable_batch_processor :: done")
        return self

    def enable_batch_processor_http(self):
        """Enable external endpoint exporter"""
        exporter = OTLPSpanExporterHTTP(endpoint=self.endpoint,
                                        headers=self.headers
                                        )
        span_processor = BatchSpanProcessor(exporter)

        self.provider.add_span_processor(span_processor)
        opentelemetry.trace.set_tracer_provider(self.provider)

        self.tracer = get_tracer(__name__)
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
