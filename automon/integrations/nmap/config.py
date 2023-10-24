from automon.log import logger
from automon.helpers import Run

log = logger.logging.getLogger(__name__)
log.setLevel(logger.ERROR)


class NmapConfig(object):
    def __init__(self, **kwargs):
        self.nmap = None

    def __repr__(self):
        if self.isReady():
            return f'{self.nmap}'
        return f'nmap not found'

    def isReady(self, **kwargs):
        check = Run('which nmap', **kwargs)

        if check.stdout:
            self.nmap = check.stdout.decode().strip()
            log.debug(f'nmap located, {self.nmap}')
            return True
        else:
            log.error(f'nmap not found')

        return False
