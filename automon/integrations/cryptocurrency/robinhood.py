from automon import log
from automon.integrations.datascience import Pandas

logger = log.logging.getLogger(__name__)
logger.setLevel(log.DEBUG)


class Robinhood:
    def __init__(self, csv):

        self.csv = None
        self.df = None
        self.is_match = None
        self.type = Robinhood.__name__

        r = RobinhoodCSV(csv)
        if r.matches:
            logger.info(f'matched {r}')
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

        self.csv = csv
        self.df = None
        self.matches = None

        if 'Provider: Robinhood Crypto LLC' in Pandas().read_csv(csv):
            logger.debug(f'matched {csv}')
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
                logger.debug(f'same {other}')
                return True
            logger.debug(f'different {other}')
        return False


class RobinhoodAPI(object):
    summary = 'https://status.robinhood.com/api/v2/summary.json'
    status = 'https://status.robinhood.com/api/v2/status.json'
    components = 'https://status.robinhood.com/api/v2/components.json'
    incidents_unresolved = 'https://status.robinhood.com/api/v2/incidents/unresolved.json'
    incidents_all = 'https://status.robinhood.com/api/v2/incidents.json'
    scheduled_maintenance_upcoming = 'https://status.robinhood.com/api/v2/scheduled-maintenances/upcoming.json'
    scheduled_maintenance_active = 'https://status.robinhood.com/api/v2/scheduled-maintenances/active.json'
    scheduled_maintenance_all = 'https://status.robinhood.com/api/v2/scheduled-maintenances.json'
