import json
import opentelemetry

from opentelemetry.util import types
from opentelemetry.trace import Status, StatusCode

from automon.helpers.loggingWrapper import LoggingClient, DEBUG, INFO

from .config import OpenTelemetryConfig

logger = LoggingClient.logging.getLogger(__name__)
logger.setLevel(DEBUG)


class OpenTelemetryClient(object):

    def __init__(self):
        self.config = OpenTelemetryConfig()

    def add_event(self, name: str, attributes: types.Attributes = None, **kwargs):
        logger.debug(dict(name=name, attributes=attributes, kwargs=kwargs))
        return self.config.opentelemetry.trace.get_current_span.add_event(
            name=name,
            attributes=attributes,
            **kwargs
        )

    def clear(self):
        logger.debug('clear')
        return self.config.clear()

    def is_ready(self):
        if self.config.is_ready():
            return True

    def get_finished_spans(self):
        logger.debug('get_finished_spans')
        return self.config.get_finished_spans()

    def pop_finished_spans(self):
        logger.debug('pop_finished_spans')
        return self.config.pop_finished_spans()

    def record_exception(self, exception: Exception):
        logger.error(f'{exception}')
        span = self.config.opentelemetry.trace.get_current_span()
        span.set_status(Status(StatusCode.ERROR))
        return span.record_exception(exception=exception)

    def start_as_current_span(
            self, name: str,
            attributes: any = None,
            **kwargs
    ):
        logger.debug(dict(name=name, attributes=attributes, kwargs=kwargs))
        return self.tracer.start_as_current_span(
            name=name,
            attributes=attributes,
            **kwargs,
        )

    def start_consumer(self):
        """adds spans from memory to queue"""
        while True:
            pass
        return

    def start_producer(self):
        """"""
        while True:
            pass
        return

    def test(self):
        with self.tracer.start_as_current_span(name='rootSpan') as trace_root:
            trace_root.add_event('AAAAAAAA')

            with self.tracer.start_as_current_span(name='childSpan') as trace_child:
                trace_child.add_event('AAAAAAAA')
                trace_child.add_event('BBBBBBBB')

            trace_root.add_event('BBBBBBBB')

        return True

    def to_dict(self):
        return [
            json.loads(span.to_json())
            for span in self.get_finished_spans()
        ]

    def to_datadog(self):
        log = []
        for span in self.to_dict():
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

    @property
    def tracer(self):
        return self.config.tracer
