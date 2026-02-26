from automon.helpers.loggingWrapper import LoggingClient
from automon.helpers import Dict

logger = LoggingClient.logging.getLogger(__name__)
logger.setLevel(LoggingClient.DEBUG)


class Tokens(Dict):
    string: str
    _ratio: int

    def __init__(self, string: str = '', ratio: int = 4):
        super().__init__()

        if not string:
            string = ''

        self.string: str = string
        self._ratio: int = ratio

    def __repr__(self):
        return f"{len(self)} tokens"

    def __len__(self):
        return self.count()

    def count(self) -> int:
        string = self.string
        ratio = self._ratio

        tokens = len(string) / ratio
        tokens = round(tokens)

        return tokens

    @property
    def count_pretty(self):
        return f"{self.count():,}"

    def sum_tokens(self, strings: list, **kwargs):
        count = sum(len(Tokens(s["content"])) for s in strings)

        logger.debug(f'[Tokens] :: {count=} :: ')
        return count

    def preview(self):
        return f"{self.string}".encode()[:50]
