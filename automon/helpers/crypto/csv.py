import os
import pandas as pd

from io import StringIO
from time import time as epoch_time
from pandas import DataFrame, Series

from automon import Logging


class CryptoCSV:
    def __init__(self, csv: str or open or StringIO = None,
                 fake_csv: str = None,
                 dataframe: DataFrame = None,
                 delimiter: str = None, **kwargs):
        """Consolidate cryptocurrency accounting

        :param csv: path to csv file
        :param fake_csv: a csv string
        :param dataframe: pandas dataframe
        :param delimiter: str
        :param kwargs: additional args for pd.read_csv()
        """
        self._log = Logging(name=CryptoCSV.__name__, level=Logging.DEBUG)

        self.df = None
        self.csv = csv

        if csv:
            self.df = pd.read_csv(csv, delimiter=delimiter, **kwargs)

        if fake_csv:
            self.df = self.csv_from_string(fake_csv, delimiter=delimiter, **kwargs)

        if dataframe is not None:
            self.df = dataframe

    def read_csv(self, file: str, delimiter: str = None, **kwargs) -> pd.read_csv:
        self._log.info(f'imported {file}')
        self.df = pd.read_csv(file, delimiter=delimiter, **kwargs)
        return self.df

    def csv_from_string(self, csv, delimiter: str = None, **kwargs) -> pd.read_csv:
        self._log.info(f'imported {csv}')
        self.df = self.read_csv(StringIO(csv), delimiter=delimiter, **kwargs)
        return self.df

    def export_csv(self, file: str = None, overwrite: bool = False,
                   incremental: bool = False,
                   index: bool = False, **kwargs):

        if self.csv:
            path, filename = os.path.split(self.csv)
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
