from automon import log

from automon.helpers.osWrapper.environ import environ

logger = log.logging.getLogger(__name__)
logger.setLevel(log.DEBUG)


class InstagramConfig(object):

    def __init__(self, login: str = None, password: str = None):
        self._login = login or environ('INSTAGRAM_LOGIN', '')
        self._password = password or environ('INSTAGRAM_PASSWORD', '')

    def __repr__(self):
        return str(dict(
            login=self.login,
            password="*" * len(self.password) if self.password else ''
        ))

    @property
    def login(self):
        if not self._login:
            logger.error(f'INSTAGRAM_LOGIN')
        return self._login

    @property
    def password(self):
        if not self._password:
            logger.error(f'INSTAGRAM_PASSWORD')
        return self._password

    @property
    def is_configured(self):
        if self.login and self.password:
            logger.info(f'{True}')
            return True
        logger.error(f'{False}')
        return False
