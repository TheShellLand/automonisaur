from sentry_sdk import set_level

from automon.helpers.os import environ


class SentryConfig(object):
    def __init__(self, dsn: str = None,
                 environment: str = None,
                 release: str = None,
                 debug: bool = False,
                 sample_rate: float = None,
                 request_bodies: str = None,
                 level: str = None):
        self.SENTRY_DSN = dsn or environ('SENTRY_DSN')
        self.SENTRY_ENVIRONMENT = environment or environ('SENTRY_ENVIRONMENT')
        self.SENTRY_RELEASE = release or environ('SENTRY_RELEASE')

        self.level = level or 'debug'
        set_level(self.level)

        # common options
        self.dsn = self.SENTRY_DSN
        self.environment = self.SENTRY_ENVIRONMENT or 'dev'
        self.release = self.SENTRY_RELEASE
        self.debug = debug
        self.sample_rate = sample_rate or 1.0
        self.max_breadcrumbs = None
        self.attach_stacktrace = None
        self.send_default_pii = None
        self.server_name = None
        self.in_app_include = None
        self.in_app_exclude = None
        self.request_bodies = request_bodies or 'always'
        self.with_locals = None
        self.ca_certs = None

        # integration configuration
        self.integrations = None
        self.default_integrations = None

        # hooks
        self.before_send = None
        self.before_breadcrumb = None

        # transport options
        self.transport = None
        self.http_proxy = None
        self.https_proxy = None
        self.shutdown_timeout = None

        # tracing options
        self.traces_sample_rate = None
        self.traces_sampler = None

    def __repr__(self):
        return f'{self.__dict__}'

    def setLevel(self, level):
        self.level = level
        return set_level(self.level)
