from automon import log
from automon.integrations.datascience import Pandas

logger = log.logging.getLogger(__name__)
logger.setLevel(log.DEBUG)


class Other:
    def __init__(self, csv):
        self.csv = csv
        self.df = OtherCSV(csv).df

    def __repr__(self):
        return f'{self.csv}'

    def __eq__(self, other):
        if self.df.equals(other.df):
            logger.debug(f'same {other}')
            return True
        logger.debug(f'different {other}')
        return False


class OtherCSV:
    def __init__(self, csv):

        self.csv = csv
        self.df = Pandas().read_csv(csv)

    def __repr__(self):
        return f'{self.df}'

    def __eq__(self, other):
        if isinstance(other, OtherCSV):
            if self.df == other.df:
                logger.debug(f'same {other}')
                return True
            logger.debug(f'different {other}')
        return False
