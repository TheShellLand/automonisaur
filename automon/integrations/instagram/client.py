from automon import Logging

from .config import InstagramConfig

log = Logging('InstagramClient', level=Logging.INFO)


class InstagramClient(object):

    def __init__(self, login: str = None, password: str = None, config: InstagramConfig = None):
        """Instagram Client"""
        self.config = config or InstagramConfig(login=login, password=password)
        self.login = self.config.login

    def _isAuthenticated(self):
        return

    def isAuthenticated(self):
        return

    def __repr__(self):
        return f'{self.__dict__}'
