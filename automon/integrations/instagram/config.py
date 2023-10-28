from automon.log import logger

from automon.helpers.osWrapper.environ import environ

log = logger.logging.getLogger(__name__)
log.setLevel(logger.DEBUG)


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
            log.error(f'INSTAGRAM_LOGIN')
        return self._login

    @property
    def password(self):
        if not self._password:
            log.error(f'INSTAGRAM_PASSWORD')
        return self._password

    @property
    def is_configured(self):
        if self.login and self.password:
            log.info(f'{True}')
            return True
        log.error(f'{False}')
        return False
