import urllib.parse

from automon.helpers.osWrapper import environ
from automon.log import logging

from .endpoints import xsoar6, xsoar8

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.DEBUG)


class XSOARConfig(object):
    """XSOAR REST API client config"""

    def __init__(
            self,
            host: str = None,
            api_key: str = None,
            api_key_id: str = None,
            verify_certs: bool = None,
            xsoar_version: int = 6
    ):
        self.host = host or environ('XSOAR_FQDN')
        self.api_key = api_key or environ('XSOAR_API_KEY')
        self.api_key_id = api_key_id or environ('XSOAR_API_KEY_ID')
        self.verify_cert = verify_certs or environ('XSOAR_VERIFY_CERTS')
        self.xsoar_version = xsoar_version or environ('XSOAR_VERSION')

        if self.host and urllib.parse.urlparse(self.host).scheme == '':
            self.host = 'https://' + urllib.parse.urlparse(self.host).path

        if self.xsoar_version == 8:
            self.api = xsoar8

        if self.xsoar_version == 6:
            self.api = xsoar6

    def is_ready(self) -> bool:
        if not self.host:
            logger.error(f'missing XSOAR_FQDN')

        if not self.api_key:
            logger.error(f'missing XSOAR_API_KEY')

        if not self.api_key_id:
            logger.error(f'missing XSOAR_API_KEY_ID')

        if self.host and self.api_key and self.api_key_id:
            return True
        return False

    @property
    def headers(self):
        return {
            'Authorization': f'{self.api_key}',
            'x-xdr-auth-id': f'{self.api_key_id}',
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
