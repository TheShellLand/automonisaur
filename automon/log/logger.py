import logging
import traceback

from logging import DEBUG, INFO, WARN, ERROR, CRITICAL, NOTSET

from automon.integrations.slack.slack_formatting import Chat, Format

# logging.basicConfig(format=log_format)

log = logging.getLogger('logger')
log.setLevel(CRITICAL)


class LogStream(object):
    """Allows logging to string
    """

    def __init__(self):
        self.logs = ''

    def write(self, string):
        self.logs += string

    def flush(self):
        pass

    def __str__(self):
        return self.logs


class Logging:
    """Standard logging to stdout
    """

    DEBUG = DEBUG
    INFO = INFO
    WARN = WARN
    ERROR = ERROR
    CRITICAL = CRITICAL
    NOTSET = NOTSET

    def __init__(self, name: __name__ = __name__, level: logging.INFO = INFO,
                 log_stream: LogStream = False):

        self.logging = logging.getLogger(name)
        self.logging.setLevel(level)

        # self.log_format = '%(levelname)s\t%(name)s\t%(module)s\t%(message)s'

        spacing = 4

        timestamp = '%(asctime)s'
        levelname = '%(levelname)s'
        modname = '[%(name)s]'
        message = '%(message)s'
        self.log_format = f'{timestamp}\t{levelname}\t{modname}\t{message}'
        # self.log_format = '%(levelname)s\t%(message)s\t%(name)s'

        logging.basicConfig(level=level, format=self.log_format)

        # TODO: need informative logging format
        # TODO: log streaming does not work
        if log_stream:
            self.stream = LogStream() if log_stream else None
            logging.basicConfig(level=level, stream=self.stream)

        log.debug('loaded')

    def error(self, msg: str = None, enable_traceback: bool = True):
        tb = traceback.format_exc()
        # tb = Chat.wrap(tb, Format.codeblock)
        if 'NoneType' not in tb and enable_traceback:
            self.logging.error(tb)

        if msg:
            return self.logging.error(msg)

    def warning(self, msg):
        return self.logging.warning(msg)

    def info(self, msg):
        return self.logging.info(msg)

    def debug(self, msg):
        return self.logging.debug(msg)

    def critical(self, msg):
        tb = traceback.format_exc()
        tb = Chat.wrap(tb, Format.codeblock)
        if 'NoneType' not in tb:
            self.logging.critical(tb)
        return self.logging.critical(msg)
