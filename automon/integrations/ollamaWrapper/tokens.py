from automon.helpers.loggingWrapper import LoggingClient
from automon.helpers import Dict

logger = LoggingClient.logging.getLogger(__name__)
logger.setLevel(LoggingClient.ERROR)


class Tokens(Dict):

    def __init__(self):
        super().__init__()

    def chr_to_tokens(self, string: str, ratio: int = 4):
        tokens = len(string) / ratio
        tokens = round(tokens)

        logger.debug(f'[chr_to_tokens] :: {tokens=} :: {ratio=}')
        return tokens

    def sum_tokens(self, strings: list, **kwargs):
        count = sum(self.chr_to_tokens(s["content"], **kwargs) for s in strings)

        logger.debug(f'[tokens] :: {count=} :: ')
        return count
