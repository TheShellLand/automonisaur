import socket
from urllib.parse import urlparse

from automon.log import Logging

log = Logging(name='Networking', level=Logging.INFO)


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
            log.debug(f'SUCCESS {url}')
            return True
        except Exception as e:
            log.error(f'FAILED {url} {e}', enable_traceback=False)
            return False

    @staticmethod
    def urlparse(url):
        return urlparse(url)
