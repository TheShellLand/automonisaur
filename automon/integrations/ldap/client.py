import os
import pandas as pd

from queue import Queue
from pandas import DataFrame
from subprocess import Popen, PIPE

from automon.log import Logging


class LdapResult(object):
    def __init__(self, output: list):
        """responses in LDIF format without comments and version

        :param output:
        """
        d = [x.split(': ') for x in output if x]
        columns = [x[0] for x in d]
        data = [[x[1]] for x in d]
        data = dict(zip(columns, data))

        self.df = pd.DataFrame(data=data, columns=columns)

    def __repr__(self) -> str:
        return f'{self.df}'


class LdapClient(object):
    def __init__(self, log_level=Logging.INFO, **kwargs):
        """run ldap commands

        :param log_level:
        :param kwargs:
        """
        self._user = os.getenv('USER')
        self._bash = self._which('bash')
        self.bin = self._which(f'ldapsearch', executable=self._bash)
        self.installed = True if self.bin else False
        # self.connected = self.check_auth()

        self.result = None
        self.results = Queue()

        self._log = Logging(name=LdapClient.__name__, level=log_level, **kwargs)

    def __repr__(self) -> str:
        return f'{self.__dict__}'

    def ldap(self, query: str = None) -> LdapResult:
        """

        :param query:
        :return: LdapResult
        """

        # f'ldapsearch -o ldif-wrap=no -x -h ldap.automon.c -b ou=groups,o=automon -LLL '
        ldap_query = f'ldapsearch -o ldif-wrap=no -x -LLL '
        ldap_query += f'"{query}"' if query else '-z 1 cn=*'

        stdout, stderr = self._run(ldap_query)

        result_ldap = LdapResult(stdout)
        self.result = {'command': ldap_query, 'result': result_ldap}
        self.results.put_nowait(self.result)

        if not result_ldap.df.empty:
            # self._log.debug(f'{result_ldap.df.iloc[0]}')
            self._log.debug(f'FOUND {query} ({self.results.qsize()})')
            # print('o', end='', flush=True)
        else:
            self._log.debug(f'UNKNOWN {query} ({self.results.qsize()})')
            # print('.', end='', flush=True)

        return result_ldap

    def ldap_cn(self, query: str, **kwargs) -> ldap:
        """ldap cn lookup"""
        return self.ldap(query=f'cn={query}', **kwargs)

    def run(self, **kwargs) -> ldap:
        """alias to ldap"""
        return self.ldap(**kwargs)

    def search(self, **kwargs) -> ldap:
        """alias to ldap"""
        return self.ldap(**kwargs)

    @staticmethod
    def to_dict(df: DataFrame) -> dict:
        """dataframe to dict"""
        return df.to_dict()

    def _which(self, cmd: str = None, **kwargs) -> str:
        """run which"""
        cmd = f'which {cmd}'
        out, err = self._run(cmd, shell=True, **kwargs)
        return out[0] if out else False

    @staticmethod
    def _run(command: list or str, shell: bool = True, executable: str = '/bin/bash') -> (list, list):
        """run shell command

        :param command:
        :param shell:
        :param executable:
        :return: Popen stdout, stderr
        """

        # TODO: migrate to Runner
        if shell:
            r = Popen(command, shell=shell, executable=executable,
                      stderr=PIPE, stdout=PIPE, stdin=PIPE).communicate()
        else:
            command = command.split()
            r = Popen(command, shell=shell, executable=executable,
                      stderr=PIPE, stdout=PIPE, stdin=PIPE).communicate()

        out = r[0].decode().splitlines()
        err = r[1].decode().splitlines()

        return out, err
