import splunklib.binding as binding

from automon.log import Logging
from automon.helpers import environ

log = Logging(name='SplunkConfig', level=Logging.DEBUG)


class SplunkConfig:
    def __init__(self,
                 host: str = None,
                 port: int = None,
                 username: str = None,
                 password: str = None,
                 verify: str = True,
                 scheme: str = 'https',
                 app: NotImplemented = None,
                 owner: NotImplemented = None,
                 token: str = None,
                 cookie: str = None,
                 timeout: int = 1):
        """Splunk config"""

        self.host = host or environ('SPLUNK_HOST', 'splunkcloud.com')
        self.port = port or environ('SPLUNK_PORT', 8089)
        self.username = username or environ('SPLUNK_USERNAME', 'admin')
        self.password = password or environ('SPLUNK_PASSWORD', 'changeme')
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
        return f'{self.__dict__}'
