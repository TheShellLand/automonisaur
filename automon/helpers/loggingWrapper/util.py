import hashlib

from .client import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.CRITICAL)


def log_secret(secret: str) -> str:
    return len(hashlib.md5(str(secret).encode()).hexdigest()) * '*'
