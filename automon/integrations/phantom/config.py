from automon import Logging
from automon.helpers.os import environ

log = Logging(name='PhantomConfig', level=Logging.DEBUG)


class PhantomConfig:
    def __init__(self, host: str = None,
                 user: str = None,
                 password: str = None,
                 auth_token: str = None):
        """Phantom Config"""

        self.host = host or environ('PHANTOM_HOST') or ''
        self.user = user or environ('PHANTOM_USER')
        self.password = password or environ('PHANTOM_PASSWORD')
        self.auth = (self.user, self.password)
        self.auth_token = auth_token or environ('PHANTOM_AUTH_TOKEN')

        self.headers = {'ph-auth-token': self.auth_token}

        if not self.host:
            log.warn(f'missing PHANTOM_HOST')

    def __repr__(self):
        return f'{self.__dict__}'
