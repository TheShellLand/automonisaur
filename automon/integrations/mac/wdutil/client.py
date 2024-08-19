from automon import log
from automon import log_secret
from automon.helpers import Run

from .config import WdutilConfig

logger = log.logging.getLogger(__name__)
logger.setLevel(level=log.DEBUG)


class WdutilClient(object):

    def __init__(self, config: WdutilConfig = None, wdutil_path: str = None):
        self.config = config or WdutilConfig(wdutil_path=wdutil_path)
        self.wdutil = self.config.wdutil_path()

        self._runner = Run()

        self.output = None

    def info(self):
        return self.run('info')

    def run(self, arg: str):
        self.config.is_ready()

        secret = f'echo {self.config.password} | '
        command = f'sudo -S {self.wdutil} {arg}'

        logger.info(f'echo {log_secret(self.config.password)} | {command}')
        run = self._runner.run(command=f'{secret}{command}', shell=True)

        output = self._runner.stdout_lines
        self.output = WdutilOutput(output=output)

        return run

    def is_ready(self):
        if self.config.is_ready():
            return True
        return False

    def help(self):
        return self.run('help')


class WdutilOutput(object):
    NETWORK: None
    WIFI: None
    BLUETOOTH: None
    AWDL: None

    def __init__(self, output: [str]):
        self._output = output

    @property
    def network(self):
        pass

    @property
    def wifi(self):
        pass

    @property
    def bluetooth(self):
        pass

    @property
    def awdl(self):
        pass
