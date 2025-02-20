from automon.helpers.subprocessWrapper import Run
from automon.helpers.loggingWrapper import LoggingClient, DEBUG, INFO, ERROR

logger = LoggingClient.logging.getLogger(__name__)
logger.setLevel(ERROR)


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
            logger.debug(f'nmap located, {self.nmap}')
            return True
        else:
            logger.error(f'nmap not found')

        return False
