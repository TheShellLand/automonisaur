import os

from automon import Logging
from automon.helpers.runner import Run
from automon.helpers.dates import Dates

from .config import NmapConfig
from .output import NmapResult


class Nmap:
    def __init__(self, command: str = None, config: NmapConfig = None, **kwargs):
        self._log = Logging(name=Nmap.__name__, level=Logging.INFO)
        self._runner = Run()

        self.config = config or NmapConfig(**kwargs)
        self.ready = self.config.ready

        self.output_file = f'nmap-{Dates.filename_timestamp()}.xml'

        self.result = None
        self.command = None
        if command:
            self.run(command=command)

    def nmap(self, command: str, **kwargs) -> bool:
        return self.run(command=command, **kwargs)

    def scan(self, command: str, **kwargs) -> bool:
        return self.run(command=command, **kwargs)

    def run(self, command: str, output: bool = True, cleanup: bool = True, **kwargs) -> bool:

        if not self.ready:
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
        stdout = self._runner.stdout
        stderr = self._runner.stderr

        if output:
            self.result = NmapResult(file=self.output_file, **kwargs)

            if cleanup:
                os.remove(self.output_file)
                self._log.info(f'deleted {self.output_file}')

        if stderr:
            self._log.error(enable_traceback=False, msg=f'{stderr.decode()}')
            return False

        return True
