from automon import log
from automon.integrations.datascience import Pandas

logger = log.logging.getLogger(__name__)
logger.setLevel(log.DEBUG)


class Coinbase:
    def __init__(self, csv):

        self.csv = None
        self.df = None
        self.is_match = None
        self.type = Coinbase.__name__

        r = CoinbaseCSV(csv)
        if r.matches:
            self.is_match = True
            self.csv = csv
            self.df = r.df

    def __repr__(self):
        return self.csv

    def __eq__(self, other):
        if self.df.equals(other.df):
            return True
        return False


class CoinbaseCSV:
    def __init__(self, csv):
        self.csv = csv
        self.df = Pandas().read_csv(csv)
        self.matches = None

    def __repr__(self):
        return CoinbaseCSV.__name__

    def __eq__(self, other):
        if self.df.equals(other.df):
            return True
        return False
