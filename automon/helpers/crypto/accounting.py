import os

from automon import Logging
from automon.helpers.crypto.robinhood import Robinhood
from automon.helpers.crypto.coinbase import Coinbase
from automon.helpers.crypto.other import Other


class CryptoAccounting:

    def __init__(self, csvs: str = None):
        self._log = Logging(name=CryptoAccounting.__name__, level=Logging.DEBUG)

        self.accounts = []

        self.supported_exchanges = [
            Robinhood,
            Coinbase
        ]

        if csvs:
            for path, folders, files in os.walk(csvs):
                for file in files:
                    extension = os.path.splitext(file)[-1].lower()
                    if '.csv' == extension:
                        file_path = os.path.join(path, file)
                        self.auto_detect(file_path)

    def auto_detect(self, csv):
        for exchange in self.supported_exchanges:
            x = exchange(csv)
            if x.is_match:
                self.accounts.append(x)
                return True

        self.accounts.append(Other(csv))
        return False

    def __repr__(self):
        return CryptoAccounting.__name__
