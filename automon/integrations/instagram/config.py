from automon.log import logger

from automon.helpers.osWrapper.environ import environ

log = logger.logging.getLogger(__name__)
log.setLevel(logger.DEBUG)


class InstagramConfig(object):

    def __init__(self, login: str = None, password: str = None):
        self._login = login or environ('INSTAGRAM_LOGIN', '')
        self._password = password or environ('INSTAGRAM_PASSWORD', '')

    @property
    def login(self):
        if self._login:
            return self._login
        log.error(f'missing INSTAGRAM_LOGIN')

    @property
    def password(self):
        if self._password:
            return self._password
        log.error(f'missin INSTAGRAM_PASSWORD')

    @property
    def is_configured(self):
        if self.login and self.password:
            log.info(f'{True}')
            return True
        log.error(f'{False}')
        return False

    def __repr__(self):
        return f'{self.login} {"*" * len(self.password)}'
