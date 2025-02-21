from automon.helpers.osWrapper import environ
from automon.helpers.loggingWrapper import LoggingClient, DEBUG

logger = LoggingClient.logging.getLogger(__name__)
logger.setLevel(DEBUG)


class GoogleGeminiConfig(object):

    def __init__(self):
        self.api_key = environ('GOOGLE_GEMINI_API_KEY')

    def __repr__(self):
        return f"[GoogleGeminiConfig] :: {self.api_key=}"

    def headers(self):
        headers = {'Content-Type': 'application/json'}
        logger.debug(f'[GoogleGeminiConfig] :: headers :: {headers=}')
        logger.info(f'[GoogleGeminiConfig] :: headers :: done')
        return headers

    def is_ready(self):
        if self.api_key:
            logger.info(f'[GoogleGeminiConfig] :: is_ready :: done')
            return True
