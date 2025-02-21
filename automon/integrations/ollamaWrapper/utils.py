import ollama

from automon.helpers.loggingWrapper import LoggingClient

logger = LoggingClient.logging.getLogger(__name__)
logger.setLevel(LoggingClient.DEBUG)


def chr_to_tokens(string: str, ratio: int = 4) -> int:
    logger.debug(f'[chr_to_tokens] :: {string=} :: {ratio=} :: >>>>')

    tokens = len(string) / ratio
    tokens = round(tokens)

    logger.debug(f'[chr_to_tokens] :: {tokens=} :: {ratio=}')
    logger.info(f'[chr_to_tokens] :: done')
    return tokens
