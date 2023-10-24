import logging
import traceback

from automon.helpers import Dates
from automon.helpers.markdown import Chat, Format

from .attributes import LogRecordAttribute

TEST = 5
DEBUG = logging.DEBUG
INFO = logging.INFO
WARN = logging.WARN
ERROR = logging.ERROR
CRITICAL = logging.CRITICAL
NOTSET = logging.NOTSET

logging.getLogger(__name__).setLevel(CRITICAL)

TIMESTAMP = True
DEFAULT_LEVEL = INFO

log_format = LogRecordAttribute(timestamp=TIMESTAMP).levelname().name_and_lineno().funcName().message()
log_format = f'{log_format}'
logging.basicConfig(level=DEFAULT_LEVEL, format=log_format)


class Callback(object):

    def __init__(self, callbacks: list):
        """Log to callbacks
        """

        self.log = Logging(name=Callback.__name__, level=Logging.DEBUG)
        self.callbacks = callbacks

    def call(self, type: str, msg: str, *args, **kwargs) -> True:
        for call in self.callbacks:
            if type == 'info':
                call.info(msg, *args, **kwargs)

            elif type == 'debug':
                call.debug(msg, *args, **kwargs)

            elif type == 'error':
                call.error(msg, *args, **kwargs)

            elif type == 'warn' or type == 'warning':
                call.warn(msg, *args, **kwargs)

            elif type == 'critical':
                call.critical(msg, *args, **kwargs)

            else:
                call.warn(f'{NotImplemented} {type} {msg}')

        return True

    def info(self, msg: str, *args, **kwargs):
        return self.call(type='info', msg=msg, *args, **kwargs)

    def debug(self, msg: str, *args, **kwargs):
        return self.call(type='debug', msg=msg, *args, **kwargs)

    def error(self, msg: str, *args, **kwargs):
        return self.call(type='error', msg=msg, *args, **kwargs)

    def warn(self, msg: str, *args, **kwargs):
        return self.call(type='warn', msg=msg, *args, **kwargs)

    def warning(self, msg: str, *args, **kwargs):
        return self.call(type='warning', msg=msg, *args, **kwargs)

    def critical(self, msg: str, *args, **kwargs):
        return self.call(type='critical', msg=msg, *args, **kwargs)


class LogStream(object):
    """Allows logging to string
    """

    def __init__(self):
        self.logs = ''

    def write(self, string):
        self.logs += string

    def flush(self):
        pass

    def __repr__(self):
        return self.logs


class Logging(object):
    """Standard logging
    """

    TEST: int = 5
    DEBUG: int = DEBUG
    INFO: int = INFO
    WARN: int = WARN
    ERROR: int = ERROR
    CRITICAL: int = CRITICAL
    NOTSET: int = NOTSET

    def __init__(self, name: str = __name__,
                 level: int = INFO,
                 file: str = None,
                 encoding: str = 'utf-8',
                 filemode: str = 'a',
                 log_stream: LogStream = False,
                 log_format: str = None,
                 callbacks: list = None,
                 timestamp: bool = True,
                 *args, **kwargs):

        self.started = Dates.now()

        self.logging = logging.getLogger(name)
        self.logging.setLevel(level)

        self.callbacks = callbacks or []

        if log_format:
            self.log_format = log_format
        else:
            self.log_format = f'{LogRecordAttribute(timestamp=timestamp).levelname().name().funcName().message()}'

        logging.basicConfig(level=level, format=self.log_format, **kwargs)

        if file:
            logging.basicConfig(filename=file, encoding=encoding, filemode=filemode, level=level,
                                format=self.log_format, **kwargs)

        # TODO: need informative logging format
        # TODO: log streaming does not work
        if log_stream:
            self.stream = LogStream() if log_stream else None
            logging.basicConfig(level=level, stream=self.stream)

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
            Callback(self.callbacks).error(msg, *args, **kwargs)
            return True

        if raise_exception:
            self.logging.error(msg, *args, **kwargs)
            Callback(self.callbacks).error(msg, *args, **kwargs)
            raise Exception(msg, *args, **kwargs)
            return True

    def warning(self, msg: any, *args, **kwargs):
        self.logging.warning(msg, *args, **kwargs)
        Callback(self.callbacks).warning(msg, *args, **kwargs)
        return True

    def warn(self, msg: any, *args, **kwargs):
        self.warning(msg, *args, **kwargs)
        Callback(self.callbacks).warn(msg, *args, **kwargs)
        return True

    def info(self, msg: any, *args, **kwargs):
        self.logging.info(msg, *args, **kwargs)
        Callback(self.callbacks).info(msg, *args, **kwargs)
        return True

    def debug(self, msg: any, *args, **kwargs):
        self.logging.debug(msg, *args, **kwargs)
        Callback(self.callbacks).debug(msg, *args, **kwargs)
        return True

    def critical(self, msg: any, *args, **kwargs):

        tb = traceback.format_exc()
        tb = Chat.wrap(tb, Format.codeblock)
        if 'NoneType' not in tb:
            self.logging.critical(tb)
            Callback(self.callbacks).critical(msg, *args, **kwargs)

        self.logging.critical(msg, *args, **kwargs)
        Callback(self.callbacks).critical(msg, *args, **kwargs)
        return True

    @staticmethod
    def now():
        return Dates.now()

    def uptime(self):
        return Dates.now() - self.started
