from automon.helpers.osWrapper import environ

from .attributes import LoggingRecordAttribute
from .client import LoggingClient, TEST, DEBUG, INFO, WARN, ERROR, CRITICAL, NOTSET
from .client import logging, LoggingClient
from .client import LoggingClient as Logging
from .stream import LoggingStream
from .util import log_secret

# log_format = f'{LoggingRecordAttribute(timestamp=True).levelname().name_and_lineno().funcName().message()}'
# log_format_opentelemetry = environ('OTEL_PYTHON_LOG_FORMAT') or '\t'.join(
#     [
#         f'%(asctime)s',
#         f'%(levelname)s',
#         f'[%(name)s]',
#         f'[%(filename)s:%(lineno)d]',
#         f'[trace_id=%(otelTraceID)s span_id=%(otelSpanID)s resource.service.name=%(otelServiceName)s trace_sampled=%(otelTraceSampled)s]',
#         f'%(funcName)s',
#         f'%(message)s']
# )
#
# try:
#     import opentelemetry
#     from opentelemetry.instrumentation.logging import LoggingInstrumentor
#
#     logging.getLogger('opentelemetry.instrumentation.instrumentor').setLevel(ERROR)
#
#     # logging.basicConfig(level=DEBUG, format=log_format_opentelemetry)
#     LoggingInstrumentor().instrument(
#         log_level=logging.DEBUG,
#         set_logging_format=True,
#         logging_format=log_format_opentelemetry)
# except:
#     logging.basicConfig(level=DEBUG, format=log_format)
