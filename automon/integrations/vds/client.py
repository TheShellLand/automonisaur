import os
import json
import base64
import requests

from .config import VdsConfig

from queue import Queue

from automon.log.logger import Logging


class VdsLdapClient(object):
    """Not implemented"""
    pass


class VdsRestClient(object):
    def __init__(self, config: VdsConfig = None):
        """VDS REST client"""

        self.config = config or VdsConfig()
        self.records = Queue()

        # test connection
        self.connected = self.check_connection()

        self._log = Logging(name=VdsRestClient.__name__, level=Logging.DEBUG)

    @staticmethod
    def check_connection():
        """check if vds server is reacheable"""
        return False

    def search(self, query: str = 'filter=cn=*', **kwargs):
        """search ldap"""
        return self._get(ldap_query=query, **kwargs)

    def search_insecure(self, query: str = 'filter=cn=*', **kwargs):
        """search ldap, ignoring ssl certificates"""
        return self._get(ldap_query=query, verify=False, **kwargs)

    def search_cafile(self, query: str = 'filter=cn=*', cafile: str = None, **kwargs):
        """search ldap, providing ssl certificate"""

        if os.path.exists(cafile):
            return self._get(ldap_query=query, verify=cafile, **kwargs)

        raise Exception(f'{cafile} not found')

    def search_paging(self, start_index: int = 0, count: int = 1000):
        """search ldap and page through all records"""

        return

    def _get(self, ldap_query: str = None, **kwargs):
        """retrieve response from server"""
        if ldap_query:
            ldap_query = f'?{ldap_query}'
        else:
            ldap_query = ''

        basic_auth = base64.b64encode(f'{self.config.user}:{self.config.password}'.encode()).decode()

        headers = {
            'Authorization': f'Basic {basic_auth}'
        }

        url = f'{self.config.uri}/{self.config.basedn}{ldap_query}'

        r = requests.get(url, headers=headers, **kwargs)

        [self._log.debug(f'results: {x}') for x in r.__dict__.items()]

        if r.status_code != 200:
            self._log.error(f'{url} {r.status_code} {r.reason}\n\n{r.content.decode()}')
            ldap_result = False
        else:
            self._log.info(f'{url} {r.status_code} {r.reason}')
            ldap_result = json.loads(r.content.decode())

        return ldap_result
