import subprocess

from pprint import pprint
from subprocess import PIPE

from automon import log
from automon.helpers.dates import Dates

from .exceptions import *

logger = log.logging.getLogger(__name__)
logger.setLevel(log.DEBUG)


class Run:

    def __init__(self, command: str = None, *args, **kwargs):
        """Run shell"""

        self.last_run = None
        self.command = ''

        self._stdout = b''
        self._stderr = b''

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
        logger.debug(command)
        if command:
            self.command = command
            return True
        return False

    @property
    def stdout(self):
        return self._stdout

    @property
    def stdout_lines(self):
        return self.stdout.decode().splitlines()

    @property
    def stderr(self):
        return self._stderr

    @property
    def stderr_lines(self):
        return self.stderr.decode().splitlines()

    def which(self, program: str, *args, **kwargs) -> bool:
        """runs which

        :param program:
        :return:
        """
        logger.debug(str(dict(
            program=program,
            args=args,
            kwargs=kwargs,
        )))
        if program:
            return self.run(command=f'which {program}', *args, **kwargs)
        return False

    def run_command(self, *args, **kwargs) -> bool:
        """alias to run"""
        logger.debug(str(dict(
            args=args,
            kwargs=kwargs,
        )))
        return self.run(*args, **kwargs)

    def run(self, command: str = None,
            text: bool = False,
            inBackground: bool = False,
            shell: bool = False,
            sanitize_command: bool = True,
            **kwargs) -> bool:

        logger.debug(str(dict(
            command=command,
            text=text,
            inBackground=inBackground,
            shell=shell,
            sanitize_command=sanitize_command,
            kwargs=kwargs,
        )))

        if command and sanitize_command:
            command = self._command(command)

        elif self.command:
            command = self.command
            if sanitize_command:
                command = self._command(self.command)

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
                        stdout=PIPE,
                        stderr=PIPE,
                        text=text,
                        shell=shell,
                        **kwargs)
                else:
                    self.call = subprocess.Popen(
                        command,
                        stdout=PIPE,
                        stderr=PIPE,
                        shell=shell,
                        **kwargs)

                stdout, stderr = self.call.communicate()
                # call.wait()

                timestamp = Dates.iso()

                self.last_run = timestamp
                self._stdout = stdout
                self._stderr = stderr
                self.returncode = self.call.returncode

                if self.returncode == 0:
                    logger.debug(str(dict(
                        stdout_KB=round(len(self.stdout) / 1024, 2),
                        stderr_KB=round(len(self.stderr) / 1024, 2),
                    )))
                    return True

        except Exception as error:
            self._stderr = f'{error}'.encode()
            logger.error(f'{error}')
            raise RuntimeError(error)

        logger.error(str(dict(
            stdout_KB=round(len(self.stdout) / 1024, 2),
            stderr_KB=round(len(self.stderr) / 1024, 2),
        )))
        return False

    def _command(self, command: str) -> list:
        self.command = command

        if isinstance(command, str):
            split_command = f'{command}'.split(' ')
            split_command = [str(x).strip() for x in split_command]
            split_command = [x for x in split_command if x]
            self.command = split_command

            for arg in split_command:
                if '|' in arg:
                    error = f'Pipes are not supported! {split_command}'
                    logger.error(error)
                    raise NotSupportedCommand(error)

        logger.debug(str(dict(
            command=self.command
        )))
        return self.command

    def __repr__(self) -> str:
        return str(dict(
            command=self.command,
            stdout=f'{round(len(self.stdout) / 1024, 2)} KB',
            stderr=f'{round(len(self.stderr) / 1024, 2)} KB',
        ))

    def __len__(self):
        return sum([len(self.stdout), len(self.stderr)])

    def __eq__(self, other):
        if isinstance(other, Run):
            self.command == other.command
            return True
        return False
