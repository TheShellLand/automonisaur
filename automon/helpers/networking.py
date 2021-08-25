import socket
from urllib.parse import urlparse

from automon import Logging

log = Logging(name='Networking', level=Logging.DEBUG)


class Networking:

    @staticmethod
    def check_connection(url):
        endpoint = urlparse(url)

        host = endpoint.hostname
        port = endpoint.port

        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1)
            s.connect((host, port))
            s.close()
            return True
        except Exception as e:
            log.error(e)
            return False

    @staticmethod
    def urlparse(url):
        return urlparse(url)
