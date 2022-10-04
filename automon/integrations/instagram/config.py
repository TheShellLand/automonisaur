from automon import Logging

from automon.helpers.osWrapper.environ import environ

log = Logging('InstagramConfig', level=Logging.INFO)


class InstagramConfig(object):

    def __init__(self, login: str = None, password: str = None):
        self.login = login or environ('INSTAGRAM_LOGIN', '')
        self.password = password or environ('INSTAGRAM_PASSWORD', '')

    def isConfigured(self):
        if self.login and self.password:
            log.info(f'OK')
            return True
        log.warn(f'BAD')
        return False

    def __repr__(self):
        if self.isConfigured():
            return f'ready'
        return f'not ready'
