from automon.helpers.datascience import Pandas


class Coinbase:
    def __init__(self, csv):
        self.df = None
        self.is_match = None
        self.type = Coinbase.__name__
        self.csv = None

        r = CoinbaseCSV(csv)
        if r.matches:
            self.df = r.df
            self.is_match = True
            self.csv = csv

    def __repr__(self):
        return self.csv

    def __eq__(self, other):
        if self.df == other.df:
            return True
        return False


class CoinbaseCSV:
    def __init__(self, csv):
        self.df = None
        self.matches = None

    def __repr__(self):
        return CoinbaseCSV.__name__

    def __eq__(self, other: Pandas):
        if self.df == other.df:
            return True
        return False
