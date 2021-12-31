import os

import splunklib.binding as binding

from automon.log import Logging


class SplunkConfig:
    def __init__(self, host: str = None, port: int = None, username: str = None,
                 password: str = None, verify: str = True, scheme: str = 'https',
                 app: NotImplemented = None, owner: NotImplemented = None,
                 token: str = None, cookie: str = None, timeout: int = 1):
        self._log = Logging(name=SplunkConfig.__name__, level=Logging.DEBUG)

        self.host = host or os.getenv('SPLUNK_HOST') or 'splunkcloud.com'
        self.port = port or os.getenv('SPLUNK_PORT') or 8090
        self.username = username or os.getenv('SPLUNK_USERNAME') or 'admin'
        self.password = password or os.getenv('SPLUNK_PASSWORD') or 'changeme'
        self.verify = verify
        self.scheme = scheme or 'https'
        self.app = app
        self.owner = owner
        self.token = token
        self.cookie = cookie
        self.handler = binding.handler(timeout=timeout)

    def info(self):
        return f'{self}'

    def __str__(self):
        return f'{self.username}@{self.scheme}://{self.host}:{self.port}'
