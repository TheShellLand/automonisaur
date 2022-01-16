from automon.log import Logging
from automon.integrations.datascience import Pandas


class Robinhood:
    def __init__(self, csv):
        self._log = Logging(name=Robinhood.__name__, level=Logging.DEBUG)

        self.csv = None
        self.df = None
        self.is_match = None
        self.type = Robinhood.__name__

        r = RobinhoodCSV(csv)
        if r.matches:
            self._log.info(f'matched {r}')
            self.is_match = True
            self.csv = csv
            self.df = r.df

    def __repr__(self):
        return f'{self.csv}'

    def __eq__(self, other):
        if self.df.equals(other.df):
            return True
        return False


class RobinhoodCSV:
    def __init__(self, csv):
        """
        Provider: Robinhood Crypto LLC,,,
        Disclaimer: ,,,,
        ,,,,
        ,,,,
        ,,,,
        ,,,,
        ASSET NAME,RECEIVED DATE,COST BASIS(USD),DATE SOLD,PROCEEDS

        """
        self._log = Logging(name=RobinhoodCSV.__name__, level=Logging.DEBUG)

        self.csv = csv
        self.df = None
        self.matches = None

        if 'Provider: Robinhood Crypto LLC' in Pandas().read_csv(csv):
            self._log.debug(f'matched {csv}')
            self.matches = True

            with open(csv) as f:
                self.df = Pandas().csv_from_string(
                    ''.join(f.readlines()[6:])
                )

    def __repr__(self):
        return f'{self.df}'

    def __eq__(self, other):
        if isinstance(other, RobinhoodCSV):
            if self.df == other.df:
                self._log.debug(f'same {other}')
                return True
            self._log.debug(f'different {other}')
        return False
