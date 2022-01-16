from automon.log import Logging
from automon.integrations.datascience import Pandas


class Other:
    def __init__(self, csv):
        self._log = Logging(name=Other.__name__, level=Logging.DEBUG)

        self.csv = csv
        self.df = OtherCSV(csv).df

    def __repr__(self):
        return f'{self.csv}'

    def __eq__(self, other):
        if self.df.equals(other.df):
            self._log.debug(f'same {other}')
            return True
        self._log.debug(f'different {other}')
        return False


class OtherCSV:
    def __init__(self, csv):
        self._log = Logging(name=OtherCSV.__name__, level=Logging.DEBUG)

        self.csv = csv
        self.df = Pandas().read_csv(csv)

    def __repr__(self):
        return f'{self.df}'

    def __eq__(self, other):
        if isinstance(other, OtherCSV):
            if self.df == other.df:
                self._log.debug(f'same {other}')
                return True
            self._log.debug(f'different {other}')
        return False
