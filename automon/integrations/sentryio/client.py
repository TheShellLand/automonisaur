import sentry_sdk

from sentry_sdk import capture_exception as _capture_exception
from sentry_sdk import capture_event as _capture_event
from sentry_sdk import capture_message as _capture_message

from .config import SentryConfig


class SentryClient(object):
    def __init__(self, dsn: str = None, config: SentryConfig = None, *args, **kwargs):
        self.config = config or SentryConfig(dsn=dsn)

        self.sentry = sentry_sdk.init(
            dsn=self.config.dsn,
            environment=self.config.environment,
            release=self.config.release,
            debug=self.config.debug,
            sample_rate=self.config.sample_rate,
            max_breadcrumbs=self.config.max_breadcrumbs,
            attach_stacktrace=self.config.attach_stacktrace,
            send_default_pii=self.config.send_default_pii,
            server_name=self.config.server_name,
            in_app_include=self.config.in_app_include,
            in_app_exclude=self.config.in_app_exclude,
            request_bodies=self.config.request_bodies,
            with_locals=self.config.with_locals,
            ca_certs=self.config.ca_certs,
            integrations=self.config.integrations,
            default_integrations=self.config.default_integrations,
            before_send=self.config.before_send,
            before_breadcrumb=self.config.before_breadcrumb,
            transport=self.config.transport,
            http_proxy=self.config.http_proxy,
            https_proxy=self.config.https_proxy,
            shutdown_timeout=self.config.shutdown_timeout,
            traces_sample_rate=self.config.traces_sample_rate,
            traces_sampler=self.config.traces_sampler,
            *args, **kwargs
        )

    def __repr__(self):
        return f'{self.__dict__}'

    def isConnected(self):
        if self.config.dsn:
            return True
        return False

    def setLevel(self, level):
        return self.config.setLevel(level)

    def capture_exception(self, exception):
        if self.isConnected():
            return _capture_exception(exception)
        return False

    def capture_event(self, message: str, level):
        if self.isConnected():
            return _capture_event(dict(
                message=message,
                level=level
            ))
        return False

    def capture_message(self, message):
        if self.isConnected():
            return _capture_message(message)
        return False

    def error(self, msg: str):
        self.setLevel('error')
        return self.capture_message(f'{msg}')

    def warning(self, msg: str):
        self.setLevel('warning')
        return self.capture_message(f'{msg}')

    def warn(self, msg: str):
        return self.warning(msg=msg)

    def info(self, msg: str):
        self.setLevel('info')
        return self.capture_message(f'{msg}')

    def debug(self, msg: str):
        self.setLevel('debug')
        return self.capture_message(f'{msg}')

    def critical(self, msg: str):
        self.setLevel('critical')
        return self.capture_message(f'{msg}')
