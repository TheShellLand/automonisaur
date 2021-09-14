from automon.helpers.datascience import Pandas


class Robinhood:
    def __init__(self, csv):
        self.df = None
        self.is_match = None
        self.type = Robinhood.__name__
        self.csv = None

        r = RobinhoodCSV(csv)
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
        self.df = None
        self.matches = None

        if 'Provider: Robinhood Crypto LLC' in Pandas().read_csv(csv):
            self.matches = True

            with open(csv) as f:
                self.df = Pandas().csv_from_string(
                    ''.join(f.readlines()[6:])
                )

    def __repr__(self):
        return RobinhoodCSV.__name__

    def __eq__(self, other: Pandas):
        if self.df == other.df:
            return True
        return False
