import json

from automon import Logging
from automon.integrations.requests import Requests

from .config import PhantomConfig
from .rest import Urls

log = Logging(name='PhantomClient', level=Logging.DEBUG)


class PhantomClient:
    def __init__(self, host: str = None,
                 user: str = None,
                 password: str = None,
                 config: PhantomConfig = None):
        """Phantom Client"""

        self.config = config or PhantomConfig(host=host, user=user, password=password)
        self.client = Requests(headers=self.config.headers)

        self.action_run = None
        self.app = None
        self.app_run = None
        self.artifacts = None
        self.asset = None
        self.cluster_node = None
        self.containers = None
        self.playbook_run = None

    def __repr__(self) -> str:
        return f'{self.__dict__}'

    def _content(self) -> bytes:
        """get result"""
        return self.client.results.content

    def _content_dict(self) -> dict:
        """convert request bytes to dict"""
        return json.loads(self._content())

    def _get(self, url: str) -> bool:
        """send get request"""
        return self.client.get(url=url, headers=self.client.headers)

    def _post(self, url: str, data: dict) -> bool:
        """send post request"""
        return self.client.post(url=url, headers=self.client.headers, data=data)

    def isConnected(self) -> bool:
        """check if client can connect"""
        if self._get(Urls().container()):
            log.info(f'Phantom client connected. '
                     f'[{self.client.results.status_code}] '
                     f'{self.config.host}')
            return True

        else:
            log.error(f'Phantom client failed.')
        return False

    def list_action_run(self, **kwargs) -> bool:
        """list action run"""
        if self._get(Urls().action_run(**kwargs)):
            self.containers = self._content_dict()
            return True
        return False

    def list_app(self, **kwargs) -> bool:
        """list app"""
        if self._get(Urls().app(**kwargs)):
            self.app = self._content_dict()
            return True
        return False

    def list_app_run(self, **kwargs) -> bool:
        """list app run"""
        if self._get(Urls().app_run(**kwargs)):
            self.app_run = self._content_dict()
            return True
        return False

    def list_artifacts(self, **kwargs) -> bool:
        """list artifacts"""
        if self._get(Urls().artifact(**kwargs)):
            self.artifacts = self._content_dict()
            return True
        return False

    def list_asset(self, **kwargs) -> bool:
        """list asset"""
        if self._get(Urls().asset(**kwargs)):
            self.asset = self._content_dict()
            return True
        return False

    def list_containers(self, **kwargs) -> bool:
        """list containers"""
        if self._get(Urls().container(**kwargs)):
            self.containers = self._content_dict()
            return True
        return False

    def list_cluster_node(self, **kwargs) -> bool:
        """list cluster node"""
        if self._get(Urls().cluster_node(**kwargs)):
            self.cluster_node = self._content_dict()
            return True
        return False

    def list_playbook_run(self, **kwargs) -> bool:
        """list cluster node"""
        if self._get(Urls().playbook_run(**kwargs)):
            self.playbook_run = self._content_dict()
            return True
        return False
