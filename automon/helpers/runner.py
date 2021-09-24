import subprocess

from subprocess import PIPE

from automon import Logging
from automon.helpers import Dates


class Run:

    def __init__(self):
        """Run shell"""
        self._log = Logging(name=Run.__name__, level=Logging.DEBUG)

        self.last_run = None
        self.command = None

        self.stdout = None
        self.stderr = None

    def set_command(self, command: str) -> bool:
        if command:
            self.command = command
            return True
        return False

    def which(self, program: str) -> bool:
        """runs which

        :param program:
        :return:
        """
        if program:
            return self.run(command=f'which {program}')
        return False

    def run_command(self, command: str, **kwargs) -> bool:
        """alias to run"""
        return self.run(command=command, **kwargs)

    def run(self, command: str = None, text: bool = False, **kwargs) -> bool:
        if command:
            command = self._command(f'{command}')

        elif self.command:
            command = self._command(self.command)

        call = subprocess.Popen(command, stdin=PIPE, stdout=PIPE, stderr=PIPE, text=text, **kwargs)
        stdout, stderr = call.communicate()
        # call.wait()

        timestamp = Dates.iso()

        self.last_run = timestamp
        self.stdout = stdout
        self.stderr = stderr

        if stdout:
            return True

        return False

    def _command(self, command: str) -> list:
        self.command = command
        return f'{command}'.split(' ')

    def __repr__(self) -> str:
        return f'{self.command}'

    def __eq__(self, other):
        if isinstance(other, Run):
            self.command == other.command
            return True
        return False
