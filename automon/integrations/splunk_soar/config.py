from automon import log
from automon.helpers.osWrapper import environ

logger = log.logging.getLogger(__name__)
logger.setLevel(log.DEBUG)


class SplunkSoarConfig:
    def __init__(self, host: str = None,
                 user: str = None,
                 password: str = None,
                 auth_token: str = None):
        """Splunk SOAR Config"""

        self.host = host or environ('SPLUNK_SOAR_HOST')
        self.user = user or environ('SPLUNK_SOAR_USER')
        self.password = password or environ('SPLUNK_SOAR_PASSWORD')
        self.auth = (self.user, self.password)
        self.auth_token = auth_token or environ('SPLUNK_SOAR_AUTH_TOKEN')

        self.headers = {'ph-auth-token': self.auth_token}

    def __repr__(self):
        return f'{self.__dict__}'

    @property
    def is_ready(self) -> bool:
        if self.host:
            return True
        logger.error(f'missing SPLUNK_SOAR_HOST')
        return False
