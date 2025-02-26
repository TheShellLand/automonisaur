import logging
import traceback

from automon.helpers.dates import Dates
from automon.helpers.osWrapper import environ
from automon.helpers.markdown import Chat, Format

from .stream import LoggingStream
# from .extended import ExtendedLogger
from .callback import LoggingCallback
from .attributes import LoggingRecordAttribute

TEST = 5
DEBUG = logging.DEBUG
INFO = logging.INFO
WARN = logging.WARN
ERROR = logging.ERROR
CRITICAL = logging.CRITICAL
NOTSET = logging.NOTSET

logger = logging.getLogger(__name__)
logger.setLevel(CRITICAL)


class LoggingClient(logging.Logger):
    """Standard logging
    """

    TEST: int = 5
    DEBUG: int = DEBUG
    INFO: int = INFO
    WARN: int = WARN
    ERROR: int = ERROR
    CRITICAL: int = CRITICAL
    NOTSET: int = NOTSET

    logging: logging = logging

    # logging.setLoggerClass(ExtendedLogger)

    log_format = f'{LoggingRecordAttribute(timestamp=True).levelname().name_and_lineno().funcName().message()}'
    log_format_opentelemetry = environ('OTEL_PYTHON_LOG_FORMAT') or '\t'.join(
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
        from opentelemetry.instrumentation.logging import LoggingInstrumentor

        logging.getLogger('opentelemetry.instrumentation.instrumentor').setLevel(ERROR)

        # logging.basicConfig(level=DEBUG, format=log_format_opentelemetry)
        LoggingInstrumentor().instrument(
            log_level=INFO,
            set_logging_format=True,
            logging_format=log_format_opentelemetry)
    except:
        logging.basicConfig(level=INFO, format=log_format)

    def __init__(self, name: str = __name__,
                 level: int = INFO,
                 file: str = None,
                 encoding: str = 'utf-8',
                 filemode: str = 'a',
                 log_stream: LoggingStream = False,
                 log_format: str = None,
                 callbacks: list = None,
                 timestamp: bool = True,
                 *args, **kwargs):

        super().__init__(name=name, level=level)

        self.started = Dates.now()

        self.logging = logging.getLogger(name)
        self.logging.setLevel(level)

        self.callbacks = callbacks or []

        if log_format:
            self.log_format = log_format
            logging.basicConfig(level=level, format=self.log_format, **kwargs)

        if file:
            logging.basicConfig(filename=file, encoding=encoding, filemode=filemode, level=level,
                                format=self.log_format, **kwargs)

        # TODO: need informative logging format
        # TODO: log streaming does not work
        if log_stream:
            self.stream = LoggingStream() if log_stream else None
            logging.basicConfig(level=level, stream=self.stream)

    def __repr__(self):
        return f'{self.logging.name}'

    def error(self, msg: any = None,
              enable_traceback: bool = True,
              raise_exception: bool = False,
              *args, **kwargs):
        tb = traceback.format_exc()
        # tb = Chat.wrap(tb, Format.codeblock)
        if 'NoneType' not in tb and enable_traceback:
            self.logging.error(tb)

        if msg and not raise_exception:
            self.logging.error(msg, *args, **kwargs)
            LoggingCallback(self.callbacks).error(msg, *args, **kwargs)
            return True

        if raise_exception:
            self.logging.error(msg, *args, **kwargs)
            LoggingCallback(self.callbacks).error(msg, *args, **kwargs)
            raise Exception(msg, *args, **kwargs)
            return True

    def warning(self, msg: any, *args, **kwargs):
        self.logging.warning(msg, *args, **kwargs)
        LoggingCallback(self.callbacks).warning(msg, *args, **kwargs)
        return True

    def warn(self, msg: any, *args, **kwargs):
        self.warning(msg, *args, **kwargs)
        LoggingCallback(self.callbacks).warn(msg, *args, **kwargs)
        return True

    def info(self, msg: any, *args, **kwargs):
        self.logging.info(msg, *args, **kwargs)
        LoggingCallback(self.callbacks).info(msg, *args, **kwargs)
        return True

    def debug(self, msg: any, *args, **kwargs):
        self.logging.debug(msg, *args, **kwargs)
        LoggingCallback(self.callbacks).debug(msg, *args, **kwargs)
        return True

    def critical(self, msg: any, *args, **kwargs):

        tb = traceback.format_exc()
        tb = Chat.wrap(tb, Format.codeblock)
        if 'NoneType' not in tb:
            self.logging.critical(tb)
            LoggingCallback(self.callbacks).critical(msg, *args, **kwargs)

        self.logging.critical(msg, *args, **kwargs)
        LoggingCallback(self.callbacks).critical(msg, *args, **kwargs)
        return True

    @staticmethod
    def now():
        return Dates.now()

    def uptime(self):
        return Dates.now() - self.started
