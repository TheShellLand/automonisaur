from automon.helpers.osWrapper import environ
from automon.integrations.google.auth import GoogleAuthConfig
from automon.helpers.loggingWrapper import LoggingClient, DEBUG, INFO

logger = LoggingClient.logging.getLogger(__name__)
logger.setLevel(DEBUG)


class GoogleGmailConfig(GoogleAuthConfig):
    def __init__(
            self,
            GOOGLE_GMAIL_ENDPOINT: str = None,
            GOOGLE_GMAIL_API_KEY: str = None,
            GOOGLE_GMAIL_USERID: str = None,
            GOOGLE_GMAIL_PASSWORD: str = None,
            serviceName: str = 'gmail',
            scopes: str = None,
            version: str = None):
        """Gmail config"""
        super().__init__(serviceName=serviceName, scopes=scopes, version=version)

        self.GOOGLE_GMAIL_ENDPOINT = (GOOGLE_GMAIL_ENDPOINT or
                                      environ('GOOGLE_GMAIL_ENDPOINT',
                                              'https://gmail.googleapis.com'))

        self.GOOGLE_GMAIL_API_KEY = (GOOGLE_GMAIL_API_KEY or
                                     environ('GOOGLE_GMAIL_API_KEY'))

        self.GOOGLE_GMAIL_USERID = (GOOGLE_GMAIL_USERID or
                                    environ('GOOGLE_GMAIL_USERID'))

        self.GOOGLE_GMAIL_PASSWORD = (GOOGLE_GMAIL_PASSWORD or
                                      environ('GOOGLE_GMAIL_PASSWORD'))

    def __repr__(self):
        return f'{self.__dict__}'
