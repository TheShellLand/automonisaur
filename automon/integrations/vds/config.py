import os


class VdsConfig(object):
    dev = 'dev_vds'
    prod = 'prod_vds'

    ldap_port = 636
    rest_port = 8090

    rest_path = 'adap'

    def __init__(self, protocol: str = None,
                 server: str = None,
                 port: int = None,
                 path: str = None,
                 user: str = None,
                 password: str = None):
        """VDS configuration"""

        self.prot = protocol or 'https'
        self.server = server or os.getenv('VDS_SERVER') or self.dev
        self.port = port or os.getenv('VDS_PORT') or self.rest_port or self.ldap_port
        self.path = path or self.rest_path

        self.user = user or os.getenv('VDS_USER')
        self.password = password or os.getenv('VDS_PASSWORD')
