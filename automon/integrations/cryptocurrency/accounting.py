import os

from automon import log

from .robinhood import Robinhood
from .coinbase import Coinbase
from .other import Other

logger = log.logging.getLogger(__name__)
logger.setLevel(log.DEBUG)


class CryptoAccounting:

    def __init__(self, csvs: str = None):

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
        logger.debug(f'supported exchanges: {self.supported_exchanges}')
        for exchange in self.supported_exchanges:
            logger.debug(f'reading exchange: {exchange}')
            x = exchange(csv)
            if x.is_match:
                logger.debug(f'exchange matched: {exchange}')
                if x not in self.accounts:
                    logger.info(f'added {x}')
                    self.accounts.append(x)
                    return True
                logger.debug(f'already added: {x}')
        else:
            o = Other(csv)
            if o not in self.accounts:
                self.accounts.append(o)
        return False

    def robinhood(self, csv):
        r = Robinhood(csv)
        if r not in self.accounts:
            self.accounts.append(r)
        return r

    def other(self, csv):
        o = Other(csv)
        if o not in self.accounts:
            self.accounts.append(o)
        return o

    def __repr__(self):
        return f'accounts: {len(self.accounts)}'
