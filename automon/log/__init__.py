from opentelemetry.instrumentation.logging import LoggingInstrumentor

from .attributes import LogRecordAttribute
from .logger import Logging, LogStream, TEST, DEBUG, INFO, WARN, ERROR, CRITICAL, NOTSET
from .logger import logging

log_format = f'{LogRecordAttribute(timestamp=True).levelname().name_and_lineno().funcName().message()}'
log_format_opentelemetry = '\t'.join(
    [
        f'%(asctime)s',
        f'%(levelname)s',
        f'[%(name)s]',
        f'[%(filename)s:%(lineno)d]',
        f'[trace_id=%(otelTraceID)s span_id=%(otelSpanID)s resource.service.name=%(otelServiceName)s trace_sampled=%(otelTraceSampled)s]',
        f'%(funcName)s',
        f'%(message)s']
)

try:
    import opentelemetry

    # logging.basicConfig(level=DEBUG, format=log_format_opentelemetry)
    LoggingInstrumentor().instrument(
        log_level=logging.DEBUG,
        set_logging_format=True,
        logging_format=log_format_opentelemetry)
except:
    logging.basicConfig(level=DEBUG, format=log_format)
