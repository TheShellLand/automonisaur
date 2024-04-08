from .attributes import LogRecordAttribute
from .logger import Logging, LogStream, TEST, DEBUG, INFO, WARN, ERROR, CRITICAL, NOTSET
from .logger import logging

log_format = f'{LogRecordAttribute(timestamp=True).levelname().name_and_lineno().funcName().message()}'
log_format_opentelemetry = f'%(asctime)s %(levelname)s [%(name)s] [%(filename)s:%(lineno)d] [trace_id=%(otelTraceID)s span_id=%(otelSpanID)s resource.service.name=%(otelServiceName)s trace_sampled=%(otelTraceSampled)s] %(message)s'.replace(
    ' ', '\t')

try:
    import opentelemetry

    logging.basicConfig(level=DEBUG, format=log_format_opentelemetry)
except:
    logging.basicConfig(level=DEBUG, format=log_format)
