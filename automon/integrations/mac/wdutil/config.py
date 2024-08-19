from automon import Run
from automon import log
from automon import environ
from automon.integrations.mac import os_is_mac

from .exceptions import *

logger = log.logging.getLogger(__name__)
logger.setLevel(level=log.DEBUG)


class WdutilConfig(object):

    def __init__(self, password: str = None, wdutil_path: str = None):
        self.password = password or environ('WDUTIL_PASSWORD')
        self._wdutil_path = wdutil_path
        self._runner = Run()

    def is_ready(self):
        if not self.password:
            logger.error(f'missing WDUTIL_PASSWORD')

        if not self.wdutil_path():
            logger.error(f'missing wdutil')

        if self.password and self.wdutil_path():
            return True

        return False

    def wdutil_path(self):
        if os_is_mac():

            if self._wdutil_path:
                return self._wdutil_path

            if self._runner.which('wdutil'):
                self._wdutil_path = self._runner.stdout.decode().strip()
                logger.info(str(dict(
                    wdutil_path=self._wdutil_path
                )))
                return self._wdutil_path

        return False
