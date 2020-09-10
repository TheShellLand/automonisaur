import os


class SplunkConfig:
    def __init__(self, host: str = os.getenv('SPLUNK_HOST'),
                 port: int = os.getenv('SPLUNK_PORT'),
                 username: str = os.getenv('SPLUNK_USERNAME'),
                 password: str = os.getenv('SPLUNK_PASSWORD')):

        self.host = host if host else 'splunkcloud.com'
        self.port = port if port else 8090
        self.username = username if username else ''
        self.password = password if password else ''

    def __str__(self):
        return f'{self.username}@{self.host}:{self.port}'
