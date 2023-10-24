import subprocess

from pprint import pprint
from subprocess import PIPE

from automon.log import logger
from automon.helpers.dates import Dates

log = logger.logging.getLogger(__name__)
log.setLevel(logger.DEBUG)


class Run:

    def __init__(self, command: str = None, *args, **kwargs):
        """Run shell"""

        self.last_run = None
        self.command = ''

        self.stdout = b''
        self.stderr = b''

        self.call = None
        self.returncode = None

        if command:
            self.run(command=command, *args, **kwargs)

    def rc(self):
        if self.call:
            self.returncode = self.call.returncode
            return self.returncode

    def Popen(self, *args, **kwargs):
        return self.run(*args, **kwargs)

    def pretty(self):
        return pprint(self.stdout.decode())

    def print(self):
        return print(self.stdout.decode())

    def set_command(self, command: str) -> bool:
        if command:
            self.command = command
            return True
        return False

    def which(self, program: str, *args, **kwargs) -> bool:
        """runs which

        :param program:
        :return:
        """
        if program:
            return self.run(command=f'which {program}', *args, **kwargs)
        return False

    def run_command(self, *args, **kwargs) -> bool:
        """alias to run"""
        return self.run(*args, **kwargs)

    def run(self, command: str = None,
            text: bool = False,
            inBackground: bool = False,
            shell: bool = False,
            sanitize_command: bool = True,
            **kwargs) -> bool:

        if command:
            if sanitize_command:
                command = self._command(command)

        elif self.command:
            command = self.command
            if sanitize_command:
                command = self._command(self.command)

        log.debug(f'[command] {command}')

        try:
            if inBackground:
                if 'text' in dir(subprocess.Popen):
                    self.call = subprocess.Popen(command, text=text, shell=shell, **kwargs)
                else:
                    self.call = subprocess.Popen(command, shell=shell, **kwargs)
                return True
            else:
                if 'text' in dir(subprocess.Popen):
                    self.call = subprocess.Popen(
                        command,
                        stdin=PIPE,
                        stdout=PIPE,
                        stderr=PIPE,
                        text=text,
                        shell=shell,
                        **kwargs)
                else:
                    self.call = subprocess.Popen(
                        command,
                        stdin=PIPE,
                        stdout=PIPE,
                        stderr=PIPE,
                        shell=shell,
                        **kwargs)

                stdout, stderr = self.call.communicate()
                # call.wait()

                timestamp = Dates.iso()

                self.last_run = timestamp
                self.stdout = stdout
                self.stderr = stderr
                self.returncode = self.call.returncode

                if self.stdout:
                    log.debug(f'[stdout] {stdout}')

                if self.stderr:
                    log.error(f'[stderr] {stderr}')

                if self.returncode == 0:
                    return True

        except Exception as e:
            self.stderr = f'{e}'.encode()
            log.error(f'{e}')

        return False

    def _command(self, command: str) -> list:
        self.command = command

        if isinstance(command, str):
            split_command = f'{command}'.split(' ')
            self.command = split_command

            for arg in split_command:
                if '|' in arg:
                    log.warning(f'Pipes are not supported! {split_command}')

        return self.command

    def __repr__(self) -> str:
        return f'{self.command} stderr: ({len(self.stderr) / 1024} Kb) stdout: ({round(len(self.stdout) / 1024, 2)} Kb)'

    def __len__(self):
        return sum([len(self.stdout), len(self.stderr)])

    def __eq__(self, other):
        if isinstance(other, Run):
            self.command == other.command
            return True
        return False
