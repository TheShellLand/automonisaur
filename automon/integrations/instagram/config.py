from automon import Logging

from automon.helpers.osWrapper.environ import environ

log = Logging('InstagramConfig', level=Logging.INFO)


class InstagramConfig(object):

    def __init__(self, login: str = None, password: str = None):
        self.login = login or environ('INSTAGRAM_LOGIN', '')
        self.password = password or environ('INSTAGRAM_PASSWORD', '')

    @property
    def is_configured(self):
        if self.login and self.password:
            log.info(f'config ready')
            return True
        log.warn(f'missing login and password')
        return False

    def __repr__(self):
        if self.is_configured:
            return f'ready'
        return f'not ready'
