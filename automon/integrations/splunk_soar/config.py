from automon.log import logger
from automon.helpers.osWrapper import environ

log = logger.logging.getLogger(__name__)
log.setLevel(logger.DEBUG)


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

        if not self.host:
            log.warning(f'missing SPLUNK_SOAR_HOST')

    def __repr__(self):
        return f'{self.__dict__}'

    @property
    def is_ready(self) -> bool:
        if self.host:
            return True
        log.warning(f'bad config')
        return False
