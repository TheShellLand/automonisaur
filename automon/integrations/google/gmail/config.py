from automon.helpers.osWrapper import environ
from automon.integrations.google.oauth import GoogleAuthConfig
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
            scopes: list = None,
            version: str = None,
            **kwargs
    ):
        """Gmail config"""
        if not scopes:
            scopes = [
                "https://www.googleapis.com/auth/gmail.addons.current.action.compose",
                "https://www.googleapis.com/auth/gmail.addons.current.message.action",
                "https://www.googleapis.com/auth/gmail.addons.current.message.metadata",
                "https://www.googleapis.com/auth/gmail.addons.current.message.readonly",
                "https://www.googleapis.com/auth/gmail.labels",
                "https://www.googleapis.com/auth/gmail.send",
                "https://www.googleapis.com/auth/gmail.readonly",
                "https://www.googleapis.com/auth/gmail.compose",
                "https://www.googleapis.com/auth/gmail.insert",
                "https://www.googleapis.com/auth/gmail.modify",
                "https://www.googleapis.com/auth/gmail.metadata",
                "https://www.googleapis.com/auth/gmail.settings.basic",
                "https://www.googleapis.com/auth/gmail.settings.sharing",
                "https://mail.google.com/"
            ]
        super().__init__(serviceName=serviceName, scopes=scopes, version=version, **kwargs)

        self.GOOGLE_GMAIL_ENDPOINT = (GOOGLE_GMAIL_ENDPOINT or
                                      environ('GOOGLE_GMAIL_ENDPOINT',
                                              'https://gmail.googleapis.com'))

    def __repr__(self):
        return f'{self.__dict__}'
