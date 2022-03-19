from automon.log import Logging
from automon.helpers.os import environ

log = Logging(name='SplunkSoarConfig', level=Logging.DEBUG)


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
            log.warn(f'missing SPLUNK_SOAR_HOST')

    def __repr__(self):
        return f'{self.__dict__}'

    def isReady(self) -> bool:
        if self.host:
            return True
        log.warn(f'bad config')
        return False
