import os
import base64
import requests

from automon.integrations.vds.config import VdsConfig


class VdsLdapClient(object):
    pass


class VdsRestClient(object):
    def __init__(self, config: VdsConfig = None):
        """VDS REST client"""

        self.config = config or VdsConfig()

        # test connection
        self.connected = self.check_connection()

    @staticmethod
    def check_connection():
        return False

    def search(self, basedn: str, params: list = None):
        return self._get(basedn, params)

    def test(self, basedn: str = 'o=*', **kwargs):
        return self._get(basedn=basedn, **kwargs)

    def test_insecure(self, basedn: str = 'o=*', **kwargs):
        return self._get(basedn=basedn, verify=False, **kwargs)

    def test_cafile(self, basedn: str = 'o=*', cafile: str = None, **kwargs):

        if os.path.exists(cafile):
            return self._get(basedn=basedn, verify=cafile, **kwargs)

        raise Exception(f'{cafile} not found')

    def _get(self, basedn: str, params: list = None, **kwargs):
        if params:
            params = '?' + '&'.join(params)
        else:
            params = ''

        uri = f'{self.config.prot}://{self.config.server}:{self.config.port}/{self.config.path}'

        basic_auth = base64.b64encode(f'{self.config.user}:{self.config.password}'.encode())

        headers = {
            'Authorization': f'Basic {basic_auth}'
        }

        url = f'{uri}/{basedn}{params}'

        r = requests.get(url, headers=headers, **kwargs)

        return r
