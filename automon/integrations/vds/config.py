import os

from automon.log import Logging


class VdsConfig(object):
    ldap_port = 636
    rest_port = 8090

    rest_path = 'adap'

    def __init__(self, protocol: str = None,
                 server: str = None,
                 port: int = None,
                 path: str = None,
                 user: str = None,
                 password: str = None,
                 basedn: str = None):
        """VDS configuration"""

        self.prot = protocol or 'https'
        self.server = server or os.getenv('VDS_SERVER')
        self.port = port or os.getenv('VDS_PORT') or self.rest_port
        self.path = path or self.rest_path

        self.user = user or os.getenv('VDS_BIND_USER')
        self.bind_user = self.user
        self.password = password or os.getenv('VDS_PASSWORD')
        self.basedn = basedn or os.getenv('VDS_BASE_DN')

        self.uri = f'{self.prot}://{self.server}:{self.port}/{self.path}'

        self._log = Logging(name=VdsConfig.__name__, level=Logging.ERROR)

        [self._log.debug(f'config: {x}') for x in self.__dict__.items()]

    def __repr__(self):
        return f'{self.prot}://{self.server}:{self.port} ({self.bind_user}) ({self.basedn})'
