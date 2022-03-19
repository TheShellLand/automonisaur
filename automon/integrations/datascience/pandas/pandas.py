import os
import pandas

from io import StringIO
from time import time as epoch_time

from automon.log import Logging

from .series import Series
from .dataframe import DataFrame


class Pandas:

    def __init__(self):
        self._log = Logging(name=Pandas.__name__, level=Logging.DEBUG)

        self.df = None
        self.csv_name = None

    def Series(self, data, *args, **kwargs) -> Series:
        return Series(data, *args, **kwargs)

    def DataFrame(self, *args, **kwargs) -> DataFrame:
        return DataFrame(*args, **kwargs)

    def read_csv(self, file: str or StringIO, delimiter: str = None, **kwargs) -> pandas.read_csv:
        """read csv"""

        if type(file) == str:
            self.csv_name = file

        self.df = pandas.read_csv(file, delimiter=delimiter, **kwargs)
        self._log.info(f'imported {file}')
        return self.df

    def csv_from_string(self, csv, delimiter: str = None, **kwargs) -> pandas.read_csv:
        """read csv from string"""

        self.df = self.read_csv(StringIO(csv), delimiter=delimiter, **kwargs)
        self._log.info(f'imported csv string {len(csv) / 1024 / 1024} MB')
        return self.df

    def export_csv(self, file: str = None, overwrite: bool = False,
                   incremental: bool = False,
                   index: bool = False, **kwargs):
        """export to csv"""

        if self.csv_name:
            path, filename = os.path.split(self.csv_name)
        else:
            path = ''
            filename = f'df.csv'
        name, ext = os.path.splitext(filename)

        if file:
            csv_export = filename

        if incremental or not overwrite:
            csv_export = os.path.join(path, f'incremental-{name}-{int(epoch_time())}{ext}')

        with open(csv_export, 'w') as f:
            f.write(self.df.to_csv(index=index, **kwargs))
            return True

        return False

    def __repr__(self):
        return f'{self.df}'

    def __eq__(self, other):
        if self.df == other.df:
            return True
        return False
