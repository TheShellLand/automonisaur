import socket
from urllib.parse import urlparse

from automon.helpers.loggingWrapper import LoggingClient, DEBUG, INFO, INFO

logger = LoggingClient.logging.getLogger(__name__)
logger.setLevel(INFO)


class Networking:

    @staticmethod
    def check_connection(url, timeout: int = 1):
        endpoint = urlparse(url)

        if not endpoint.hostname:
            endpoint = urlparse(f'x://{url}')

        host = endpoint.hostname
        port = endpoint.port

        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(timeout)
            s.connect((host, port))
            s.close()
            logger.debug(f'SUCCESS {url}')
            return True
        except Exception as e:
            logger.error(f'{url} {e}')
            return False

    @staticmethod
    def urlparse(url):
        return urlparse(url)
