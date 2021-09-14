from automon.helpers.datascience import Pandas


class Other:
    def __init__(self, csv):
        self.df = OtherCSV(csv).df
        self.csv = csv

    def __repr__(self):
        return self.csv


class OtherCSV:
    def __init__(self, csv):
        self.df = Pandas().read_csv(csv)

    def __repr__(self):
        return OtherCSV.__name__

    def __eq__(self, other):
        if self.df == other.df:
            return True
        return False
