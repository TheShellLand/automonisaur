import re
import os
import json
import base64
import urllib3
import requests

from .config import VdsConfig

from queue import Queue

from automon.log import Logging

# disable insecure ssl warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


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

        self._log = Logging(name=VdsRestClient.__name__, level=Logging.INFO)

    @staticmethod
    def check_connection():
        """check if vds server is reacheable"""
        return False

    def search(self, ldap_filter: str = 'filter=cn=*', **kwargs):
        """search ldap"""
        return self._get(ldap_filter=ldap_filter, **kwargs)

    def search_insecure(self, ldap_filter: str = 'filter=cn=*', **kwargs):
        """search ldap, ignoring ssl certificates"""
        return self._get(ldap_filter=ldap_filter, verify=False, **kwargs)

    def search_cafile(self, ldap_filter: str = 'filter=cn=*', cafile: str = None, **kwargs):
        """search ldap, providing ssl certificate"""

        if os.path.exists(cafile):
            return self._get(ldap_filter=ldap_filter, verify=cafile, **kwargs)

        raise Exception(f'{cafile} not found')

    def search_all(self, ldap_filter: str = 'filter=cn=*', page_size: int = 10, cafile: str = None, **kwargs):
        """page through all results

        'cookie' Value
        cookie: Record the value in the ‘cookie’ field. This value defines a search parameter that will
            be used to display the next page of search results. If the value in the ‘cookie’ field is “null”,
            the last page of search results has been reached; there are no more pages to retrieve.


        page_size: number of records per page. max 500
        """

        initial_query = ldap_filter
        query = f'{initial_query}{self._paging(page_size=page_size)}'
        cookie = ''

        while 1:
            if not cookie:
                if cafile:
                    records = self.search_cafile(ldap_filter=query, cafile=cafile, **kwargs)
                else:
                    records = self.search_insecure(ldap_filter=query, **kwargs)
            else:
                paging_query = f'{query}{old_cookie}'
                if cafile:
                    records = self.search_cafile(ldap_filter=paging_query, cafile=cafile, **kwargs)
                else:
                    records = self.search_insecure(ldap_filter=paging_query, **kwargs)

            [self.records.put_nowait(x) for x in records['resources']]

            self._log.info(f'Records: {self.records.qsize()}')

            # need to fix cookie 'hostname' to reflect vds config server
            # otherwise get request fails to match hostname to ssl hostname
            # &cookie=localhost=NTEyNDIzODcw
            cookie = records['cookie']

            if cookie == 'null':
                break

            c = re.search('=(.*)', cookie)
            b64 = c.groups()[-1]

            old_cookie = f'&cookie={cookie}'

            # TODO: fix issue when using ssl verify
            # with ssl verify, paging, and given 'old_cookie', 'request.get' fails because request uses the IP
            # instead of the hostname. This fails the certificate check, because hostnames
            fix_cookie = f'&cookie={self.config.server}={b64}'

        return self.records

    def _paging(self, page_size: int = 100):
        """limit ldap by paging

        'totalResults' Value
        -1: The number of entries returned by the search exceeds the default size limit (1000 entries).
        -2: A next page of search results is available to be displayed. This value is displayed only when
            performing a paged search.
        -3: The last page of search results has been reached.
        Any other value: The total number of entries that were matched. This value is displayed only if
            the parameter SizeLimit is set to 0.


        page_size: If the PageSize option is used, ‘startIndex’, ‘count’ and ‘sizeLimit’ options will be ignored.
        """
        return f'&pageSize={page_size}'

    def _indexing(self, start_index: int = 0, count: int = 10, size_limit: int = 100):
        """limit ldap by indexing"""
        return f'&sizeLimit={size_limit}&startIndex={start_index}&count={count}'

    def _get(self, ldap_filter: str = None, **kwargs):
        """retrieve response from server"""
        if ldap_filter:
            ldap_filter = f'?{ldap_filter}'
        else:
            ldap_filter = ''

        basic_auth = base64.b64encode(f'{self.config.user}:{self.config.password}'.encode()).decode()

        headers = {
            'Authorization': f'Basic {basic_auth}'
        }

        url = f'{self.config.uri}/{self.config.basedn}{ldap_filter}'

        self._log.debug(f'query: {url}')

        try:
            r = requests.get(url, headers=headers, **kwargs)
        except Exception as e:
            raise Exception(e)

        [self._log.debug(f'results: {x}') for x in r.__dict__.items()]

        if r.status_code != 200:
            self._log.error(f'{url} {r.status_code} {r.reason}\n\n{r.content.decode()}')
            ldap_result = False
        else:
            self._log.debug(f'{r.status_code} {r.reason} {url}')
            ldap_result = json.loads(r.content.decode())

        return ldap_result
