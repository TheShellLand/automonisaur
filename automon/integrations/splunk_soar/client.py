import json
import functools

from automon import Logging
from automon.integrations.requests import Requests

from .rest import Urls
from .artifact import Artifact
from .container import Container
from .config import SplunkSoarConfig
from .results import ResultsContainer

log = Logging(name='SplunkSoarClient', level=Logging.DEBUG)
Logging(name='RequestsClient', level=Logging.DEBUG)


class SplunkSoarClient:
    def __init__(self, host: str = None,
                 user: str = None,
                 password: str = None,
                 config: SplunkSoarConfig = None):
        """Splunk SOAR Client"""

        self.config = config or SplunkSoarConfig(host=host, user=user, password=password)
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
        """convert request.content to dict"""
        return json.loads(self._content())

    def _get(self, url: str) -> bool:
        """send get request"""
        return self.client.get(url=url, headers=self.client.headers)

    def _isConnected(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            if self.config.isReady():
                return func(self, *args, **kwargs)
            return False

        return wrapper

    def _delete(self, url: str) -> bool:
        """send get request"""
        return self.client.delete(url=url, headers=self.client.headers)

    def _post(self, url: str, data: dict) -> bool:
        """send post request"""
        return self.client.post(url=url, headers=self.client.headers, data=data)

    @_isConnected
    def create_artifact(
            self,
            container_id,
            cef=None,
            cef_types=None,
            data=None,
            description=None,
            end_time=None,
            ingest_app_id=None,
            kill_chain=None,
            label=None,
            name=None,
            owner_id=None,
            run_automation=None,
            severity=None,
            source_data_identifier=None,
            start_time=None,
            tags=None,
            type=None,
            *args, **kwargs) -> Artifact:
        """Create artifact"""

        artifact = Artifact(
            dict(cef=cef,
                 cef_types=cef_types,
                 container_id=container_id,
                 data=data,
                 description=description,
                 end_time=end_time,
                 ingest_app_id=ingest_app_id,
                 kill_chain=kill_chain,
                 label=label,
                 name=name,
                 owner_id=owner_id,
                 run_automation=run_automation,
                 severity=severity,
                 source_data_identifier=source_data_identifier,
                 start_time=start_time,
                 tags=tags,
                 type=type)
        )

        if self._post(Urls().artifact(*args, **kwargs), data=artifact.to_json()):
            if self.client.results.status_code == 200:
                id = self.client.to_dict()['id']
                log.info(f'artifact created. {artifact} {self.client.to_dict()}')
                return self.list_artifact(artifact_id=id)
            else:
                existing_artifact_id = self.client.to_dict()['existing_artifact_id']
                log.info(f'artifact exists. {artifact} {self.client.to_dict()}')
                return self.list_artifact(artifact_id=existing_artifact_id)

        log.error(f'create artifact. {self.client.to_dict()}', enable_traceback=False)
        return False

    @_isConnected
    def create_container(
            self,
            label,
            name,
            artifacts=None,
            asset_id=None,
            close_time=None,
            custom_fields=None,
            data=None,
            description=None,
            due_time=None,
            end_time=None,
            ingest_app_id=None,
            kill_chain=None,
            owner_id=None,
            role_id=None,
            run_automation=None,
            sensitivity=None,
            severity=None,
            source_data_identifier=None,
            start_time=None,
            open_time=None,
            status=None,
            tags=None,
            tenant_id=None,
            container_type=None,
            template_id=None,
            authorized_users=None,
            *args, **kwargs) -> Container:
        """Create container"""

        container = Container(
            dict(label=label,
                 name=name,
                 artifacts=artifacts,
                 asset_id=asset_id,
                 close_time=close_time,
                 custom_fields=custom_fields,
                 data=data,
                 description=description,
                 due_time=due_time,
                 end_time=end_time,
                 ingest_app_id=ingest_app_id,
                 kill_chain=kill_chain,
                 owner_id=owner_id,
                 role_id=role_id,
                 run_automation=run_automation,
                 sensitivity=sensitivity,
                 severity=severity,
                 source_data_identifier=source_data_identifier,
                 start_time=start_time,
                 open_time=open_time,
                 status=status,
                 tags=tags,
                 tenant_id=tenant_id,
                 container_type=container_type,
                 template_id=template_id,
                 authorized_users=authorized_users)
        )

        if self._post(Urls().container(*args, **kwargs), data=container.to_json()):
            if self.client.results.status_code == 200:
                id = self.client.to_dict()['id']
                log.info(f'container created. {container} {self.client.to_dict()}')
                return self.get_container(container_id=id)
        log.error(f'create container. {self.client.to_dict()}', enable_traceback=False)
        return False

    @_isConnected
    def delete_container(self, container_id, *args, **kwargs):
        """Delete containers"""
        assert isinstance(container_id, int)

        if self._delete(Urls().container(identifier=container_id, *args, **kwargs)):
            if self.client.results.status_code == 200:
                log.info(f'container deleted: {container_id}')
                return True
        log.error(f'delete container: {container_id}. {self.client.to_dict()}', enable_traceback=False)
        return False

    def isConnected(self) -> bool:
        """check if client can connect"""
        if self.config.isReady():
            if self._get(Urls().container()):
                log.info(f'client connected '
                         f'{self.config.host} '
                         f'[{self.client.results.status_code}] ')
                return True

        else:
            log.warn(f'client not connected')
        return False

    @_isConnected
    def list_artifact(self, artifact_id: int = None, **kwargs) -> bool:
        """list action run"""
        if self._get(Urls().artifact(identifier=artifact_id, **kwargs)):
            request = self._content_dict()
            if artifact_id:
                return Artifact(request)
            artifacts = [Artifact(a) for a in request['data']]
            return artifacts
        return []

    @_isConnected
    def list_action_run(self, **kwargs) -> bool:
        """list action run"""
        if self._get(Urls().action_run(**kwargs)):
            self.containers = self._content_dict()
            return True
        return False

    @_isConnected
    def list_app(self, **kwargs) -> bool:
        """list app"""
        if self._get(Urls().app(**kwargs)):
            self.app = self._content_dict()
            return True
        return False

    @_isConnected
    def list_app_run(self, **kwargs) -> bool:
        """list app run"""
        if self._get(Urls().app_run(**kwargs)):
            self.app_run = self._content_dict()
            return True
        return False

    @_isConnected
    def list_artifacts(self, **kwargs) -> bool:
        """list artifacts"""
        if self._get(Urls().artifact(**kwargs)):
            self.artifacts = self._content_dict()
            return True
        return False

    @_isConnected
    def list_asset(self, **kwargs) -> bool:
        """list asset"""
        if self._get(Urls().asset(**kwargs)):
            self.asset = self._content_dict()
            return True
        return False

    @_isConnected
    def get_container(self, container_id: int = None, **kwargs) -> Container:
        if self._get(Urls().container(identifier=container_id, **kwargs)):
            request = self._content_dict()
            container = Container(request)
            log.info(f'get container: {container}')
            return container

        log.error(f'container not found: {container_id}', enable_traceback=False)
        return False

    @_isConnected
    def list_containers(self,
                        page: int = None,
                        page_size: int = 1000,
                        *args, **kwargs) -> ResultsContainer:
        """list containers"""

        url = Urls().container(page=page, page_size=page_size, *args, **kwargs)
        if self._get(url):
            request = self._content_dict()
            containers = ResultsContainer(request)
            log.info(f'list containers: {len(containers.data)}')
            return containers
        log.error(f'no containers', enable_traceback=False)
        return ResultsContainer()

    @_isConnected
    def list_containers_generator(self, page: int = 0, page_size: int = None, **kwargs) -> [Container]:
        """Generator for paging through containers"""

        page = page

        while True:
            request = self.list_containers(page=page, page_size=page_size)
            if request.data:
                containers = request.data
                num_pages = request.num_pages
                log.info(f'{page}/{num_pages} ({round(page / num_pages * 100, 2)}%)')

                if page > num_pages:
                    log.info(f'list container finished')
                    return True

                yield containers
                page += 1

            elif request.data == []:
                log.info(f'{page}/{num_pages} ({round(page / num_pages * 100, 2)}%)')
                log.info(f'list container finished. {request}')
                return True

            elif request.data is None:
                log.error(f'list container failed', enable_traceback=True)
                return False

            else:
                log.info(f'no containers. {request}')
                return True

        return False

    @_isConnected
    def list_cluster_node(self, **kwargs) -> bool:
        """list cluster node"""
        if self._get(Urls().cluster_node(**kwargs)):
            self.cluster_node = self._content_dict()
            return True
        return False

    @_isConnected
    def list_playbook_run(self, **kwargs) -> bool:
        """list cluster node"""
        if self._get(Urls().playbook_run(**kwargs)):
            self.playbook_run = self._content_dict()
            return True
        return False

    @_isConnected
    def list_vault(self, identifier=None, **kwargs) -> bool:
        """list cluster node"""
        if self._get(Urls().vault(identifier=identifier, **kwargs)):
            self.playbook_run = self._content_dict()
            return True
        return False
