import os
import warnings
import opentelemetry
from opentelemetry.trace import set_tracer_provider

from automon.helpers.osWrapper import environ
from automon.helpers.loggingWrapper import LoggingClient, DEBUG, INFO

logger = LoggingClient.logging.getLogger(__name__)
logger.setLevel(DEBUG)


class DatadogOpenTelemetryConfig(object):

    def __init__(self, host: str = 'https://api.datadoghq.com', api_key: str = None, app_key: str = None):
        self.host = host or environ('DD_SITE')
        self.api_key = api_key or environ('DD_API_KEY')
        self.app_key = app_key or environ('DD_APP_KEY')

        self.set_tracer_provider = False
        self.ddtrace_provider = None

    def is_ready(self):
        if self.set_tracer_provider:
            return True
        logger.error(f'run {DatadogOpenTelemetryConfig.__name__}.{self.instrumentation.__name__}')

    def instrumentation(self):

        warnings.warn(f"This breaks pytest --log-cli-level DEBUG")

        # Must be set before ddtrace is imported!
        os.environ["DD_TRACE_OTEL_ENABLED"] = "true"

        import ddtrace.opentelemetry

        self.ddtrace_provider = ddtrace.opentelemetry.TracerProvider()
        opentelemetry.trace.set_tracer_provider(self.ddtrace_provider)
        self.set_tracer_provider = True

        return self.set_tracer_provider
