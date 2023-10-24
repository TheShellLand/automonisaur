import json
import base64
import functools

from typing import Optional

from automon.log import logger
from automon.integrations.requestsWrapper import Requests

from .action_run import ActionRun
from .artifact import Artifact
from .config import SplunkSoarConfig
from .container import Container
from .vault import Vault
from .rest import Urls
from .responses import (
    AppRunResults,
    AppRunResponse,
    CancelPlaybookResponse,
    CloseContainerResponse,
    CreateContainerAttachmentResponse,
    CreateContainerResponse,
    GenericResponse,
    PlaybookRun,
    Response,
    RunPlaybookResponse,
    UpdatePlaybookResponse,
    VaultResponse
)

log = logger.logging.getLogger(__name__)
log.setLevel(logger.DEBUG)

logger.logging.getLogger('RequestsClient').setLevel(logger.DEBUG)


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
        self.asset = None
        self.containers = None
        self.playbook_run = None

    def __repr__(self) -> str:
        return f'{self.__dict__}'

    def _content(self) -> bytes:
        """get result"""
        if self.client.results:
            return self.client.results.content
        return b''

    def _content_dict(self) -> dict:
        """convert request.content to dict"""
        if self._content():
            return json.loads(self._content())
        return {}

    def _get(self, url: str) -> bool:
        """send get request"""
        return self.client.get(url=url, headers=self.client.headers)

    def _is_connected(func):
        """wrapper for connection checking"""

        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            if self.config.is_ready:
                if self._get(Urls.container(page_size=1)):
                    return func(self, *args, **kwargs)
            return False

        return wrapper

    def _delete(self, url: str) -> bool:
        """send get request"""
        return self.client.delete(url=url, headers=self.client.headers)

    def _post(self, url: str, data: dict) -> bool:
        """send post request"""
        return self.client.post(url=url, headers=self.client.headers, data=data)

    @_is_connected
    def close_container(self, container_id: int, **kwargs) -> Optional[CloseContainerResponse]:
        """Set container status to closed"""
        data = dict(status='closed')
        if self._post(Urls.container(identifier=container_id, **kwargs), data=json.dumps(data)):
            if self.client.results.status_code == 200:
                response = CloseContainerResponse(self._content_dict())
                log.info(f'container closed: {response}')
                return response

        log.error(msg=f'close failed. {self.client.to_dict()}')

    @_is_connected
    def cancel_playbook_run(
            self,
            playbook_run_id: int = None,
            cancel: bool = True, **kwargs) -> CancelPlaybookResponse:
        """Cancel playbook run"""
        data = dict(cancel=cancel)
        data = json.dumps(data)

        if self._post(Urls.playbook_run(identifier=playbook_run_id, **kwargs), data=data):
            if self.client.results.status_code == 200:
                response = CancelPlaybookResponse(self._content_dict())
                log.info(f'cancel playbook run: {response}')
                return response

        log.error(f'cancel failed: {playbook_run_id} {self.client.to_dict()}')

    @_is_connected
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

        if self._post(Urls.artifact(*args, **kwargs), data=artifact.to_json()):
            if self.client.results.status_code == 200:
                id = self.client.to_dict()['id']
                log.info(f'artifact created. {artifact} {self.client.to_dict()}')
                return self.get_artifact(artifact_id=id)
            else:
                existing_artifact_id = self.client.to_dict()['existing_artifact_id']
                log.info(f'artifact exists. {artifact} {self.client.to_dict()}')
                return self.get_artifact(artifact_id=existing_artifact_id)

        log.error(f'create artifact. {self.client.to_dict()}')
        return False

    @_is_connected
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

        if self._post(Urls.container(*args, **kwargs), data=container.to_json()):
            if self.client.results.status_code == 200:
                response = CreateContainerResponse(self.client.to_dict())
                log.info(f'container created. {container} {response}')
                return response
        log.error(f'create container. {self.client.to_dict()}')
        return False

    @staticmethod
    def base64_encode(data: bytes, **kwargs) -> str:
        encode = base64.b64encode(data, **kwargs)
        decode = encode.decode()
        return decode

    @_is_connected
    def create_container_attachment(
            self,
            container_id: int,
            file_name: str,
            file_content: bytes,
            metadata: dict = None, **kwargs) -> Optional[CreateContainerAttachmentResponse]:
        """Create container attachment"""

        if metadata:
            metadata = json.dumps(metadata)

        file_content = self.base64_encode(file_content)

        data = json.dumps(dict(
            container_id=container_id,
            file_name=file_name,
            file_content=file_content,
            metadata=metadata
        ))

        if self._post(Urls.container_attachment(**kwargs), data=data):
            response = CreateContainerAttachmentResponse(self.client.to_dict())
            log.info(f'create attachment: {response}')
            return response

        log.error(f'create attachment failed.')

    @_is_connected
    def create_vault(
            self,
            file_location,
            container_id=None,
            file_name=None,
            metadata=None,
            trace=False, **kwargs) -> Vault:
        """Add vault object"""

        data = Vault(dict(
            container=container_id,
            file_location=file_location,
            file_name=file_name,
            metadata=metadata,
            trace=trace
        ))

        if self._post(Urls.vault_add(identifire=data.id, **kwargs), data=data.to_json()):
            response = Vault(self._content_dict())
            log.info(msg=f'add vault: {response}')
            return response

        log.error(msg=f'add vault failed.')

    @_is_connected
    def delete_container(self, container_id, *args, **kwargs):
        """Delete containers"""
        assert isinstance(container_id, int)

        if self._delete(Urls.container(identifier=container_id, *args, **kwargs)):
            if self.client.results.status_code == 200:
                log.info(f'container deleted: {container_id}')
                return True
        log.error(f'delete container: {container_id}. {self.client.to_dict()}')
        return False

    def is_connected(self) -> bool:
        """check if client can connect"""
        if self.config.is_ready:
            if self._get(Urls.container(page_size=1)):
                log.info(f'client connected '
                         f'{self.config.host} '
                         f'[{self.client.results.status_code}] ')
                return True

        else:
            log.warning(f'client not connected')
        return False

    @_is_connected
    def filter_vault(self, filter: str, page_size: int = None, **kwargs) -> [Vault]:
        """Filter for matching vault files"""
        matches = []

        for sublist in self.list_vault_generator(page_size=page_size, **kwargs):
            for vault in sublist:
                if filter in vault.meta.values():
                    matches.append(vault)
                elif filter in vault.names:
                    matches.append(vault)
                elif filter in vault.__dict__.values():
                    matches.append(vault)

        return matches

    @_is_connected
    def generic_delete(self, api: str, **kwargs) -> Optional[GenericResponse]:
        """Make generic delete calls"""
        if self._delete(Urls.generic(api=api, **kwargs)):
            response = GenericResponse(self._content_dict())
            log.info(f'generic delete {api}: {response}')
            return response

        log.error(f'failed generic delete {api}')

    @_is_connected
    def generic_get(self, api: str, **kwargs) -> Optional[GenericResponse]:
        """Make generic get calls"""
        if self._get(Urls.generic(api=api, **kwargs)):
            response = GenericResponse(self._content_dict())
            log.info(f'generic get {api}: {response}')
            return response

        log.error(f'failed generic get {api}')

    @_is_connected
    def generic_post(self, api: str, data: dict, **kwargs) -> Optional[GenericResponse]:
        """Make generic post calls"""
        if self._post(Urls.generic(api=api, **kwargs), data=data):
            response = GenericResponse(self._content_dict())
            log.info(f'generic post {api}: {response}')
            return response

        log.error(f'failed generic post {api}')

    @_is_connected
    def get_action_run(self, action_run_id: int = None, **kwargs) -> ActionRun:
        """Get action run"""
        if self._get(Urls.action_run(identifier=action_run_id, **kwargs)):
            action_run = ActionRun(self._content_dict())
            log.info(f'get action run: {action_run}')
            return action_run

        log.error(f'action run not found: {action_run_id}')
        return ActionRun()

    @_is_connected
    def get_artifact(self, artifact_id: int = None, **kwargs) -> Artifact:
        """Get artifact"""
        if self._get(Urls.artifact(identifier=artifact_id, **kwargs)):
            artifact = Artifact(self._content_dict())
            log.info(f'get artifact: {artifact}')
            return artifact

        log.error(f'artifact not found: {artifact_id}')
        return Artifact()

    @_is_connected
    def get_container(self, container_id: int = None, **kwargs) -> Container:
        """Get container"""
        if self._get(Urls.container(identifier=container_id, **kwargs)):
            container = Container(self._content_dict())
            log.info(f'get container: {container}')
            return container

        log.error(f'container not found: {container_id}')
        return Container()

    @_is_connected
    def get_playbook_run(self, playbook_run_id: str, **kwargs) -> Optional[PlaybookRun]:
        """Get running playbook"""
        if self._get(Urls.playbook_run(identifier=playbook_run_id, **kwargs)):
            response = PlaybookRun(self._content_dict())

            if response.status != 'failed':
                log.info(f'playbook run: {response}')
                return response

            log.error(f'playbook run failed: {response.message_to_dict}')
            return response

        log.error(f'playbook failed: {self.client.errors}')

    @_is_connected
    def get_vault(self, vault_id: int, **kwargs) -> Optional[Vault]:
        """Get vault object"""
        if self._get(Urls.vault(identifier=vault_id, **kwargs)):
            if self.client.results.status_code == 200:
                response = Vault(self._content_dict())
                log.info(msg=f'get vault: {response}')
                return response

        log.error(msg=f'get vault failed: {self.client.to_dict()}')

    @_is_connected
    def list_artifact(self, **kwargs) -> Response:
        """list artifacts"""
        if self._get(Urls.artifact(**kwargs)):
            response = Response(self._content_dict())
            log.info(f'list artifacts: {response.count}')
            return response

        return Response()

    @_is_connected
    def list_action_run(self, **kwargs) -> bool:
        """list action run"""
        if self._get(Urls.action_run(**kwargs)):
            self.containers = self._content_dict()
            return True
        return False

    @_is_connected
    def list_app(self, **kwargs) -> bool:
        """list app"""
        if self._get(Urls.app(**kwargs)):
            self.app = self._content_dict()
            return True
        return False

    @_is_connected
    def list_app_run(
            self,
            page: int = None,
            page_size: int = None, **kwargs) -> bool:
        """list app run"""
        if self._get(Urls.app_run(page=page, page_size=page_size, **kwargs)):
            self.app_run = AppRunResponse(self._content_dict())
            response = AppRunResponse(self._content_dict())
            response.data = [AppRunResults(x) for x in response.data]
            log.info(f'list app runs, page: {page} page_size: {page_size}, {response.summary()}')
            self.app_run = response
            return response
        return False

    @_is_connected
    def list_app_run_generator(
            self,
            page: int = 0,
            page_size: int = None,
            max_pages: int = None, **kwargs) -> AppRunResults or bool:
        """Generator for paging through app runs"""

        page = page

        while True:
            response = self.list_app_run(page=page, page_size=page_size, **kwargs)
            if response.data:
                app_runs = response.data
                num_pages = response.num_pages
                log.info(f'{page}/{num_pages} ({round(page / num_pages * 100, 2)}%)')

                if page >= num_pages or page >= max_pages:
                    log.info(f'list app runs finished')
                    return True

                yield app_runs
                page += 1

            elif response.data == []:
                log.info(f'{page}/{num_pages} ({round(page / num_pages * 100, 2)}%)')
                log.info(f'list app runs finished. {response}')
                return True

            elif response.data is None:
                log.error(f'list app runs failed')
                return False

            else:
                log.info(f'no app runs. {response}')
                return True

        return False

    @_is_connected
    def list_app_run_by_playbook_run(
            self,
            playbook_run: int,
            page: int = None,
            page_size: int = None, **kwargs) -> bool:
        """list app run by playbook run"""

        app_runs = []

        for app_run in self.list_app_run_generator(page=page, page_size=page_size, **kwargs):
            if app_run.playbook_run == playbook_run:
                app_runs.append(app_run)

        return app_runs

    @_is_connected
    def list_artifacts(
            self,
            page: int = None,
            page_size: int = 1000, **kwargs) -> Response:
        """list artifacts"""
        if self._get(Urls.artifact(page=page, page_size=page_size, **kwargs)):
            response = Response(self._content())
            log.info(f'list artifacts: {len(response.data)}')
            return response
        return Response()

    @_is_connected
    def list_artifact_generator(
            self,
            page: int = 0,
            page_size: int = None,
            max_pages: int = None, **kwargs) -> [Container]:
        """Generator for paging through artifacts"""

        page = page

        while True:
            response = self.list_containers(page=page, page_size=page_size, **kwargs)
            if response.data:
                containers = [Container(x) for x in response.data]
                num_pages = response.num_pages
                log.info(f'{page}/{num_pages} ({round(page / num_pages * 100, 2)}%)')

                if page >= num_pages or page >= max_pages:
                    log.info(f'list container finished')
                    return True

                yield containers
                page += 1

            elif response.data == []:
                log.info(f'{page}/{num_pages} ({round(page / num_pages * 100, 2)}%)')
                log.info(f'list container finished. {response}')
                return True

            elif response.data is None:
                log.error(f'list container failed')
                return False

            else:
                log.info(f'no containers. {response}')
                return True

        return False

    @_is_connected
    def list_asset(self, **kwargs) -> Response:
        """list asset"""
        if self._get(Urls.asset(**kwargs)):
            response = Response(self._content_dict())
            log.info(f'list assets: {len(response.data)}')
            return response
        return Response()

    @_is_connected
    def list_containers(
            self,
            page: int = None,
            page_size: int = 1000,
            *args, **kwargs) -> Response:
        """list containers"""

        url = Urls.container(page=page, page_size=page_size, *args, **kwargs)
        if self._get(url):
            response = Response(self._content_dict())
            log.info(f'list containers: {len(response.data)}')
            return response
        log.error(f'no containers')
        return Response()

    @_is_connected
    def list_containers_generator(
            self,
            page: int = 0,
            page_size: int = None,
            max_pages: int = None, **kwargs) -> [Container]:
        """Generator for paging through containers"""

        page = page
        i = 0

        while True:
            if max_pages and i > max_pages:
                break

            response = self.list_containers(
                page=page,
                page_size=page_size, **kwargs
            )

            i += 1
            if response.data:
                containers = [Container(x) for x in response.data]
                num_pages = response.num_pages
                log.info(f'container page {page}/{num_pages} ({round(page / num_pages * 100, 2)}%)')

                if page > num_pages:
                    log.info(f'list container finished')
                    break

                yield containers
                page += 1

            elif response.data == []:
                log.info(f'{page}/{num_pages} ({round(page / num_pages * 100, 2)}%)')
                log.info(f'list container finished. {response}')
                break

            elif response.data is None:
                log.error(f'list container failed')
                break

            else:
                log.info(f'no containers. {response}')
                break

        return []

    @_is_connected
    def list_cluster_node(self, **kwargs) -> Optional[dict]:
        """List cluster node"""
        if self._get(Urls.cluster_node(**kwargs)):
            cluster_node = self._content_dict()
            return cluster_node

    @_is_connected
    def list_vault(self, **kwargs) -> Optional[VaultResponse]:
        """List vault"""
        if self._get(Urls.vault(**kwargs)):
            response = VaultResponse(self._content_dict())
            log.info(msg=f'list vault: {response}')
            return response

        log.error(msg=f'list vault failed.')

    @_is_connected
    def list_vault_generator(
            self,
            page: int = 0,
            page_size: int = None,
            max_pages: int = None, **kwargs) -> [Vault]:
        """Generator for paging through vaults"""
        i = 0

        while True:
            if max_pages and i >= max_pages:
                break

            response = self.list_vault(
                page=page,
                page_size=page_size, **kwargs
            )

            i += 1
            if response.data:
                vaults = [Vault(x) for x in response.data]
                num_pages = response.num_pages
                log.info(f'vault page {page}/{num_pages} ({round(page / num_pages * 100, 2)}%)')

                if page > num_pages:
                    log.info(f'list vault finished')
                    break

                yield vaults
                page += 1

            elif response.data == []:
                log.info(f'{page}/{num_pages} ({round(page / num_pages * 100, 2)}%)')
                log.info(f'list vault finished. {response}')
                break

            elif response.data is None:
                log.error(f'list vault failed')
                break

            else:
                log.info(f'no vaults. {response}')
                break

        return []

    @_is_connected
    def update_playbook(
            self,
            playbook_id: int = None,
            active: bool = None,
            cancel_runs: bool = False,
            **kwargs) -> Optional[UpdatePlaybookResponse]:
        """Update playbook active state"""
        data = dict(
            active=active,
            cancel_runs=cancel_runs
        )
        data = json.dumps(data)
        if self._post(Urls.playbook(identifier=playbook_id, **kwargs), data=data):
            if self.client.results.status_code == 200:
                response = UpdatePlaybookResponse(self._content_dict())
                log.info(f'update playbook: {data}')
                return response

        log.error(f'update failed: {self.client.to_dict()}')

    @_is_connected
    def run_playbook(
            self,
            container_id: int,
            playbook_id: int,
            scope: str = 'all',
            run: bool = True,
            **kwargs) -> Optional[RunPlaybookResponse]:
        """Run playbook on a container"""
        data = dict(
            container_id=container_id,
            playbook_id=playbook_id,
            scope=scope,
            run=run
        )
        data = json.dumps(data)
        if self._post(Urls.playbook_run(**kwargs), data=data):
            if self.client.results.status_code == 200:
                response = RunPlaybookResponse(self._content_dict())
                log.info(f'run playbook: {data}')
                return response

        log.error(f'run failed: {self.client.to_dict()}')
