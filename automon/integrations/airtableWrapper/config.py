from automon.helpers.osWrapper import environ
from automon.helpers.loggingWrapper import LoggingClient, DEBUG, INFO

logger = LoggingClient.logging.getLogger(__name__)
logger.setLevel(DEBUG)


class AirtableConfig(object):

    def __init__(
            self,
            AIRTABLE_TOKEN: str = None,
    ):
        self.AIRTABLE_TOKEN: str = AIRTABLE_TOKEN or environ('AIRTABLE_TOKEN')

    def is_ready(self):
        if self.AIRTABLE_TOKEN:
            return True
        return False

    def headers(self):
        return {
            "Authorization": f"Bearer {self.AIRTABLE_TOKEN}",
            "Content-Type": "application/json",
        }
