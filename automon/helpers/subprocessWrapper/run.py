import subprocess

from pprint import pprint

from automon import log
from automon.helpers.dates import Dates

from .exceptions import *

logger = log.logging.getLogger(__name__)
logger.setLevel(log.DEBUG)


class Run:
    command: str

    def __init__(self, command: str = None, **kwargs):
        """Run shell"""

        self.last_run = None
        self.command = command

        self._stdout = b''
        self._stderr = b''

        self.call = None
        self.returncode = None

        if command:
            self.run(command=command, **kwargs)

    def rc(self):
        if self.call:
            self.returncode = self.call.returncode
            return self.returncode

    def Popen(self, *args, **kwargs):
        return self.run(*args, **kwargs)

    def pretty(self):
        template = f"""stdout:
{self.stdout.decode()}
stderr:
{self.stderr.decode()}"""
        pprint(template)

    def print(self):
        template = f"""stdout:
{self.stdout.decode()}

stderr:
{self.stderr.decode()}"""
        print(template)

    def set_command(self, command: str) -> bool:
        logger.debug(command)
        if command:
            self.command = command
            return True
        return False

    @property
    def stdout(self) -> bytes:
        if type(self._stdout) is str:
            return str(self._stdout).encode()

        return self._stdout

    @property
    def stdout_lines(self):
        return self.stdout.decode().splitlines()

    @property
    def stderr(self) -> bytes:
        if type(self._stderr) is str:
            return str(self._stderr).encode()

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
            which=program,
            args=args,
            kwargs=kwargs,
        )))
        return self.run(command=f'which {program}', *args, **kwargs)

    def run_command(self, *args, **kwargs) -> bool:
        """alias to run"""
        logger.debug(str(dict(
            args=args,
            kwargs=kwargs,
        )))
        return self.run(*args, **kwargs)

    def run(
            self,
            command: str,
            pipe: bool = False,
            text: bool = False,
            shell: bool = False,
            sanitize_command: bool = True,
            **kwargs
    ) -> bool:

        if not pipe:
            self.command = command

        if sanitize_command and not shell:
            command = self.sanitize_command(command)

        if not command:
            logger.error(str(dict(
                command=command,
                text=text,
                shell=shell,
                sanitize_command=sanitize_command,
                kwargs=kwargs,
            )))
            raise SyntaxError(f'command cannot be empty, {command}')

        logger.debug(str(dict(
            command=command,
            text=text,
            shell=shell,
            sanitize_command=sanitize_command,
            kwargs=kwargs,
        )))

        try:

            self.call = subprocess.Popen(
                args=command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=text,
                shell=shell,
                **kwargs)

            stdout, stderr = self.call.communicate()
            # self.call.wait()

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

    def sanitize_command(self, command: str) -> [str]:

        if isinstance(command, str):

            if '|' in command:
                command = self.sanitize_command_pipe(command=command)
                command = [self.sanitize_command_spaces(command=cmd) for cmd in command]
            else:
                command = self.sanitize_command_spaces(command=command)

        logger.debug(str(dict(
            command=command
        )))
        return command

    def sanitize_command_pipe(self, command: str) -> [str]:
        """support for shell command piping"""
        error = f'Pipes are not supported! To use run(shell=True). {command}'
        logger.error(error)
        raise NotSupportedCommand(error)

        split_command = f'{command}'.split('|')
        return split_command

    def sanitize_command_spaces(self, command: str) -> [str]:
        split_command = f'{command}'.split(' ')
        split_command = [str(x).strip() for x in split_command]
        split_command = [x for x in split_command if x]
        return split_command

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
