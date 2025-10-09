import automon.integrations.requestsWrapper

from .config import PanoramaConfig
from .api.v10 import *


class PanoramaClient(object):

    def __init__(self, panorama_host: str = None, panorama_api_key: str = None):
        self.config = PanoramaConfig(panorama_host=panorama_host, panorama_api_key=panorama_api_key)
        self.host = self.config.PANORAMA_HOST
        self.headers = None

        self._requests = automon.integrations.requestsWrapper.RequestsClient()

    def _api_url(self, endpoint) -> str:
        return f'{self.host}/{endpoint}'

    @property
    def is_ready(self) -> bool:
        if self.config.is_ready:
            self.headers = self.config.auth_header()
            return True
        return False

    def _request_get(self, url, params=None, **kwargs) -> bool:
        url = self._api_url(url)

        headers = self.headers
        request = self._requests.get(url=url, params=params, headers=headers, **kwargs)
        return request

    def _request_post(self, url, params=None, **kwargs) -> bool:
        url = self._api_url(url)

        headers = self.headers
        request = self._requests.post(url=url, params=params, headers=headers, **kwargs)
        return request

    def _request_delete(self):
        pass

    def _request_update(self):
        pass

    def get_api_key(self):
        """To generate an API key, make a POST request to the firewall’s hostname or IP addresses using the
        administrative credentials and type=keygen:
        """

        url = Api().keygen
        request = self._request_post(url=url)

        if request:
            self.config.PANORAMA_API_KEY = self._requests.text
        else:
            error = self._requests.content
            raise Exception(f'[PanoramaClient] :: get_api_key :: ERROR :: {error=}')

        return self

    def get_firewall_device(self):
        return self

    def get_firewall_devices(self):
        return self

    def get_firewall_rules(self, firewall_device: str):
        return self
