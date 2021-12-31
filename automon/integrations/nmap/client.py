import os

from automon.log import Logging
from automon.helpers.runner import Run
from automon.helpers.dates import Dates

from .config import NmapConfig
from .output import NmapResult


class Nmap(object):
    def __init__(self, command: str = None, config: NmapConfig = None, *args, **kwargs):
        self._log = Logging(name=Nmap.__name__, level=Logging.INFO)
        self._runner = Run()

        self.config = config or NmapConfig()
        self.output_file = f'nmap-{Dates.filename_timestamp()}.xml'

        self.result = None
        self.command = str()
        self.error = bytes()

        self._stdout = None
        self._stderr = None
        self._returncode = None

        if command:
            self.run(command=command, *args, **kwargs)

    def __repr__(self):
        if self.result:
            return f'{self.command} ({round(len(self.result) / 1024, 2)} Kb)'
        if self.command:
            return f'{self.command}'
        if self.isReady():
            return f'Ready to scan'
        return f'Not able to scan'

    def __len__(self):
        if self.result:
            return len(self.result)
        return 0

    def isReady(self):
        return self.config.isReady()

    def pretty(self):
        return print(self._runner.stdout.decode())

    def nmap(self, command: str, **kwargs) -> bool:
        return self.run(command=command, **kwargs)

    def scan(self, command: str, **kwargs) -> bool:
        return self.run(command=command, **kwargs)

    def run(self, command: str, output: bool = True, cleanup: bool = True, **kwargs) -> bool:

        if not self.isReady():
            self._log.error(enable_traceback=False, msg=f'nmap not found')
            return False

        nmap_command = f'{self.config.nmap} '

        if output:
            nmap_output = f'-oX {self.output_file}'
            nmap_command += f'{nmap_output} '

        nmap_command += f'{command}'

        self._log.info(f'running {nmap_command}')
        self._runner.run(nmap_command, **kwargs)
        self._log.debug(f'finished')

        self.command = nmap_command
        self._stdout = self._runner.stdout
        self._stderr = self._runner.stderr
        self._returncode = self._runner.returncode

        self.error = self._stderr

        if output:
            self.result = NmapResult(file=self.output_file, **kwargs)

            if cleanup:
                os.remove(self.output_file)
                self._log.info(f'deleted {self.output_file}')

        if self._stderr:
            self._log.error(enable_traceback=False, msg=f'{self._stderr.decode()}')
            return False

        return True
