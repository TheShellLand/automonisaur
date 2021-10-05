from automon import Logging
from automon.helpers.runner import Run


class NmapConfig(object):
    def __init__(self, **kwargs):
        self._log = Logging(name=NmapConfig.__name__, level=Logging.ERROR)

        self.nmap = None
        self.ready = None

        check = Run()
        check.run('which nmap', **kwargs)

        if check.stdout:
            self.nmap = check.stdout.decode().strip()
            self.ready = True
            self._log.debug(f'nmap located, {self.nmap}')
        else:
            self._log.error(f'nmap not found', enable_traceback=False)

    def __repr__(self):
        if self.ready:
            return f'{self.nmap}'
        return f'nmap not found'
