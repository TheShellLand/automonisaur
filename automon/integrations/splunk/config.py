import os


class SplunkConfig:
    def __init__(self, host: str = os.getenv('SPLUNK_HOST'),
                 port: int = os.getenv('SPLUNK_PORT'),
                 username: str = os.getenv('SPLUNK_USERNAME'),
                 password: str = os.getenv('SPLUNK_PASSWORD'),
                 verify: str = True,
                 scheme: str = 'https',
                 app: NotImplemented = None,
                 owner: NotImplemented = None,
                 token: str = None,
                 cookie: str = None):

        self.host = host if host else 'splunkcloud.com'
        self.port = port if port else 8090
        self.username = username if username else ''
        self.password = password if password else ''
        self.verify = verify
        self.scheme = scheme if scheme else 'https'
        self.app = app
        self.owner = owner
        self.token = token
        self.cookie = cookie

    def info(self):
        return f'{self}'

    def __str__(self):
        return f'{self.username}@{self.scheme}://{self.host}:{self.port}'
