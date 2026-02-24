import ollama

from automon.helpers.loggingWrapper import LoggingClient

logger = LoggingClient.logging.getLogger(__name__)
logger.setLevel(LoggingClient.ERROR)


def chr_to_tokens(string: str, ratio: int = 4) -> int:
    logger.debug(f'[chr_to_tokens] :: {string=} :: {ratio=}')

    tokens = len(string) / ratio
    tokens = round(tokens)

    logger.debug(f'[chr_to_tokens] :: {tokens=} :: {ratio=}')
    return tokens


def sum_tokens(strings: list, **kwargs) -> int:
    count = sum(chr_to_tokens(s["content"], **kwargs) for s in strings)

    logger.debug(f'[tokens] :: {strings=} :: ')
    return count
