from .attributes import LogRecordAttribute
from .logger import Logging, LogStream, TEST, DEBUG, INFO, WARN, ERROR, CRITICAL, NOTSET
from .logger import logging

log_format = f'{LogRecordAttribute(timestamp=True).levelname().name_and_lineno().funcName().message()}'
logging.basicConfig(level=DEBUG, format=log_format)
