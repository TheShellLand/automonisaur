import os
import csv

from automon import log
from automon.helpers import Run

logger = log.logging.getLogger(__name__)
logger.setLevel(level=log.DEBUG)


class KeepassEntry(object):
    ENTRY_FORMAT: dict = {
        'Group': 0,
        'Title': 1,
        'Username': 2,
        'Password': 3,
        'URL': 4,
        'Notes': 5,
        'TOPT': 6,
        'Icon': 7,
        'Last Modified': 8,
        'Created': 9,
    }

    def __init__(self, cvs_row: list):
        self.Group: str = cvs_row[self.ENTRY_FORMAT['Group']]
        self.Title: str = cvs_row[self.ENTRY_FORMAT['Title']]
        self.Username: str = cvs_row[self.ENTRY_FORMAT['Username']]
        self.Password: str = cvs_row[self.ENTRY_FORMAT['Password']]
        self.URL: str = cvs_row[self.ENTRY_FORMAT['URL']]
        self.Notes: str = cvs_row[self.ENTRY_FORMAT['Notes']]
        self.TOPT: str = cvs_row[self.ENTRY_FORMAT['TOPT']]
        self.Icon: str = cvs_row[self.ENTRY_FORMAT['Icon']]
        self.LastModified: str = cvs_row[self.ENTRY_FORMAT['Last Modified']]
        self.Created: str = cvs_row[self.ENTRY_FORMAT['Created']]

        self.pass_name = '/'.join(f'{self.Group}/{self.Title}'.split('/')[1:])

    def __str__(self):
        return f'{self.pass_name} :: {self.Username} :: {self.URL}'

    def to_pass(self):
        return f"""{self.Password}
Title: {self.Title}
Username: {self.Username}
URL: {self.URL}
TOPT: {self.TOPT}
Icon: {self.Icon}
Created: {self.Created}
Last Modified: {self.LastModified}
Notes: {self.Notes}
"""


class KeepassClient(object):

    def __init__(self):
        self.database_csv_path = None

    def read_database_csv(self, database_csv_path: str, delimiter: str = ',', quotechar: str = '"') -> [KeepassEntry]:
        if self.set_database_csv_path(database_csv_path=database_csv_path):
            logger.debug(f'KeepassClient :: read_database_csv :: read')
            with open(self.database_csv_path, 'r') as csvfile:
                return [KeepassEntry(pw) for pw in csv.reader(csvfile, delimiter=delimiter, quotechar=quotechar)][1:]

        raise OSError(f'KeepassClient :: read_database_csv :: ERROR :: {database_csv_path}')

    def set_database_csv_path(self, database_csv_path: str) -> True:
        if os.path.exists(database_csv_path):
            self.database_csv_path = database_csv_path
            logger.debug(
                f'KeepassClient :: set_database_csv_path :: {database_csv_path} :: {os.stat(database_csv_path)}')
            return True

        raise FileNotFoundError(f'KeepassClient :: set_database_csv_path :: ERROR :: {database_csv_path}')


class PassClient(object):

    def __init__(self):
        self.runner = Run()

    def save(self, pass_name: str, password: str):
        with open('password_temp.txt', 'w') as password_file:
            password_file.write(password)

        command = (f'pass insert -f -m "{pass_name}" < password_temp.txt')
        self.runner.run(command=command, shell=True)
