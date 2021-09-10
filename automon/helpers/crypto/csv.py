import pandas as pd

from io import StringIO
from pandas import DataFrame, Series

from automon import Logging


class CryptoCSV:
    def __init__(self, csv: str or open or StringIO = None,
                 fake_csv: str = None,
                 dataframe: DataFrame = None,
                 delimiter: str = None, **kwargs):
        self._log = Logging(name=CryptoCSV.__name__, level=Logging.DEBUG)

        self.df = None

        if csv:
            self.df = pd.read_csv(csv, delimiter=delimiter, **kwargs)

        if fake_csv:
            self.df = self.csv_from_string(fake_csv, delimiter=delimiter, **kwargs)

        if dataframe is not None:
            self.df = dataframe

    def read_csv(self, file: str, delimiter: str = None, **kwargs) -> pd.read_csv:
        self._log.info(f'imported {file}')
        return pd.read_csv(file, delimiter=delimiter, **kwargs)

    def csv_from_string(self, csv, delimiter: str = None, **kwargs) -> pd.read_csv:
        self._log.info(f'imported {csv}')
        return self.read_csv(StringIO(csv), delimiter=delimiter, **kwargs)

    def __repr__(self):
        return f'{self.df}'
