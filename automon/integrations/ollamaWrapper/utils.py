import ollama

from automon.helpers.loggingWrapper import LoggingClient

logger = LoggingClient.logging.getLogger(__name__)
logger.setLevel(LoggingClient.ERROR)


def chr_to_tokens(string: str, ratio: int = 4) -> int:
    logger.debug(f'[chr_to_tokens] :: {string=} :: {ratio=} :: >>>>')

    tokens = len(string) / ratio
    tokens = round(tokens)

    logger.debug(f'[chr_to_tokens] :: {tokens=} :: {ratio=}')
    logger.info(f'[chr_to_tokens] :: done')
    return tokens


def sum_tokens(strings: list, **kwargs) -> int:
    logger.debug(f'[tokens] :: {strings=} :: >>>>')

    count = sum(chr_to_tokens(s["content"], **kwargs) for s in strings)

    logger.debug(f'[tokens] :: {strings=} :: ')
    logger.info(f'[tokens] :: {strings=} :: done')
    return count
