import os

try:
    import opentelemetry
    import queue

    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import SimpleSpanProcessor, BatchSpanProcessor
    from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter as OTLPSpanExporterHTTP
    from opentelemetry.trace import set_tracer_provider, get_tracer, get_tracer_provider, get_current_span
except Exception:
    import queue


    class TracerProvider:
        def add_span_processor(self, *args, **kwargs):
            pass


    class SimpleSpanProcessor:
        def __init__(self, *args, **kwargs):
            pass


    class BatchSpanProcessor:
        def __init__(self, *args, **kwargs):
            pass


    class InMemorySpanExporter:
        def __init__(self, *args, **kwargs):
            pass

        def get_finished_spans(self):
            return []

        def clear(self):
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


    def get_current_span(*args, **kwargs):
        return None


    class _DummyTrace:
        get_current_span = staticmethod(get_current_span)
        set_tracer_provider = staticmethod(set_tracer_provider)
        get_tracer = staticmethod(get_tracer)


    class _DummyOtel:
        trace = _DummyTrace()


    opentelemetry = _DummyOtel()

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
        self.exporter = None
        self.tracer: opentelemetry.trace.Tracer = None

        self.queue_consumer = queue.Queue()
        self.queue_producer = queue.Queue()

    @property
    def headers(self):
        if self.OTEL_EXPORTER_OTLP_TOKEN is not None:
            return {
                'Authorization': f"{Networking.quote(self.OTEL_EXPORTER_OTLP_TOKEN)}"
            }
        return None

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

        provider = self.provider
        provider.add_span_processor(span_processor)
        set_tracer_provider(provider)

        tracer = get_tracer(__name__)

        self.exporter = exporter
        self.tracer = tracer

        logger.debug(f"enable_memory_processor :: {tracer=} :: {__name__=}")
        logger.info("enable_memory_processor :: done")
        return self

    def enable_batch_processor_grpc(self):
        """Enable external endpoint exporter via gRPC"""
        exporter = OTLPSpanExporter(
            endpoint=self.endpoint,
            insecure=self.insecure,
            headers=self.headers
        )
        span_processor = BatchSpanProcessor(exporter)

        provider = self.provider
        provider.add_span_processor(span_processor)
        set_tracer_provider(provider)

        tracer = get_tracer(__name__)

        self.exporter = exporter
        self.tracer = tracer

        logger.info("enable_batch_processor_grpc :: done")
        return self

    def enable_batch_processor_http(self):
        """Enable external endpoint exporter via HTTP"""
        exporter = OTLPSpanExporterHTTP(
            endpoint=self.endpoint,
            headers=self.headers
        )
        span_processor = BatchSpanProcessor(exporter)

        provider = self.provider
        provider.add_span_processor(span_processor)
        set_tracer_provider(provider)

        tracer = get_tracer(__name__)

        self.exporter = exporter
        self.tracer = tracer

        logger.info("enable_batch_processor_http :: done")
        return self

    def clear(self):
        if self.exporter is not None and hasattr(self.exporter, 'clear'):
            return self.exporter.clear()
        return None

    @property
    def get_current_span(self):
        return self.opentelemetry.trace.get_current_span()

    def is_ready(self):
        if self.tracer is not None:
            return True
        logger.error("No tracers enabled")
        return False

    def get_finished_spans(self) -> list:
        if self.exporter is not None and hasattr(self.exporter, 'get_finished_spans'):
            return self.exporter.get_finished_spans()
        return []

    def pop_finished_spans(self):
        """Snapshot finished spans and reset the in-memory buffer."""
        spans = list(self.get_finished_spans())
        self.clear()
        return spans
