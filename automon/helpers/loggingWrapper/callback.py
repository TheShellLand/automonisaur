from .client import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.CRITICAL)


class LoggingCallback(object):

    def __init__(self, callbacks: list):
        """Log to callbacks
        """

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
