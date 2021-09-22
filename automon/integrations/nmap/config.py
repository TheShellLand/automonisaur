from automon import Logging
from automon.helpers.runner import Run


class NmapConfig:
    def __init__(self, **kwargs):
        self._log = Logging(name=NmapConfig.__name__, level=Logging.ERROR)

        self.nmap = None
        self.ready = None

        self._runner = Run()
        self._runner.run('which nmap', **kwargs)

        if self._runner.stdout:
            self.nmap = self._runner.stdout.decode().strip()
            self.ready = True
            self._log.debug(f'nmap located, {self.nmap}')
