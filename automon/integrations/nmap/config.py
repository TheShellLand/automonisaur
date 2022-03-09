from automon.log import Logging
from automon.helpers import Run


class NmapConfig(object):
    def __init__(self, **kwargs):
        self._log = Logging(name=NmapConfig.__name__, level=Logging.ERROR)

        self.nmap = None

    def __repr__(self):
        if self.isReady():
            return f'{self.nmap}'
        return f'nmap not found'

    def isReady(self, **kwargs):
        check = Run('which nmap', **kwargs)

        if check.stdout:
            self.nmap = check.stdout.decode().strip()
            self._log.debug(f'nmap located, {self.nmap}')
            return True
        else:
            self._log.error(f'nmap not found', enable_traceback=False)

        return False
