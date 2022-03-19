from os import getenv

from automon.log import Logging

log = Logging(name='GmailConfig', level=Logging.DEBUG)


class GmailConfig:
    def __init__(self, endpoint: str = None,
                 api_key: str = None,
                 user: str = None,
                 password: str = None):
        """Gmail config"""
        self.endpoint = endpoint or getenv('GMAIL_ENDPOINT') or 'https://gmail.googleapis.com'
        self.api_key = api_key or getenv('GMAIL_API_KEY')
        self.userId = user or getenv('GMAIL_USER')
        self.password = password or getenv('GMAIL_PASSWORD')

    def __repr__(self):
        return f'{self.__dict__}'
