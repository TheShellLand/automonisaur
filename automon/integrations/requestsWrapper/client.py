import json
import requests

from automon import log
from .config import RequestsConfig

logger = log.logging.getLogger(__name__)
logger.setLevel(log.DEBUG)


class RequestsClient(object):
    def __init__(self, url: str = None, data: dict = None, headers: dict = None,
                 config: RequestsConfig = None):
        """Wrapper for requests library"""

        self.config = config or RequestsConfig()

        self.url: str = url
        self.data: dict = data
        self.errors: bytes = b''
        self.headers: dict = headers
        self.response = None
        self.requests = requests
        self.session = self.requests.Session()

    def __repr__(self):
        return f'{self.__dict__}'

    def __len__(self):
        if self.content:
            len(self.content)

    async def _log_result(self):
        if self.status_code == 200:
            msg = [
                self.response.request.method,
                self.response.url,
                f'{round(len(self.content) / 1024, 2)} KB',
                f'{self.status_code}',
            ]
            msg = ' '.join(msg)
            return logger.debug(msg)

        msg = [
            self.response.request.method,
            self.response.url,
            f'{round(len(self.content) / 1024, 2)} KB',
            f'{self.status_code}',
            f'{self.content}'
        ]

        msg = ' '.join(msg)
        return logger.error(msg)

    async def _params(self, url, data, headers):
        if url is None:
            url = self.url

        if data is None:
            data = self.data

        if headers is None:
            headers = self.headers

        self.url = url
        self.data = data
        self.headers = headers
        return url, data, headers

    @property
    def content(self):
        if 'content' in dir(self.response):
            return self.response.content

    async def content_to_dict(self):
        return await self.to_dict()

    async def delete(
            self,
            url: str = None,
            data: dict = None,
            headers: dict = None,
            **kwargs
    ) -> bool:
        """requests.delete"""

        url, data, headers = await self._params(url, data, headers)

        try:
            self.response = self.session.delete(url=url, data=data, headers=headers, **kwargs)
            await self._log_result()

            if self.status_code == 200:
                return True

            return False
        except Exception as e:
            self.errors = e
            logger.error(f'delete failed. {e}')
        return False

    async def get(
            self,
            url: str = None,
            data: dict = None,
            headers: dict = None,
            **kwargs
    ) -> bool:
        """requests.get"""

        url, data, headers = await self._params(url, data, headers)

        try:
            self.response = self.session.get(url=url, data=data, headers=headers, **kwargs)

            logger.debug(
                f'{self.response.url} '
                f'{round(len(self.content) / 1024, 2)} KB '
                f'{self.status_code}'
            )

            if self.status_code == 200:
                return True

            self.errors = self.content

            return False
        except Exception as e:
            self.errors = e
            logger.error(f'{e}')
        return False

    async def patch(
            self,
            url: str = None,
            data: dict = None,
            headers: dict = None,
            **kwargs
    ) -> bool:
        """requests.patch"""

        url, data, headers = await self._params(url, data, headers)

        try:
            self.response = self.session.patch(url=url, data=data, headers=headers, **kwargs)

            logger.debug(
                f'{self.response.url} '
                f'{round(len(self.content) / 1024, 2)} KB '
                f'{self.status_code}'
            )

            if self.status_code == 200:
                return True

            self.errors = self.content

            return False
        except Exception as e:
            self.errors = e
            logger.error(f'patch failed. {e}')
        return False

    async def post(
            self,
            url: str = None,
            data: dict = None,
            headers: dict = None,
            **kwargs
    ) -> bool:
        """requests.post"""

        url, data, headers = await self._params(url, data, headers)

        try:
            self.response = self.session.post(url=url, data=data, headers=headers, **kwargs)

            logger.debug(
                f'{self.response.url} '
                f'{round(len(self.content) / 1024, 2)} KB '
                f'{self.status_code}'
            )

            if self.status_code == 200:
                return True

            self.errors = self.content

            return False
        except Exception as e:
            self.errors = e
            logger.error(f'post failed. {e}')
        return False

    async def put(
            self,
            url: str = None,
            data: dict = None,
            headers: dict = None,
            **kwargs
    ) -> bool:
        """requests.put"""

        url, data, headers = await self._params(url, data, headers)

        try:
            self.response = self.session.put(url=url, data=data, headers=headers, **kwargs)

            logger.debug(
                f'{self.response.url} '
                f'{round(len(self.content) / 1024, 2)} KB '
                f'{self.status_code}'
            )

            if self.status_code == 200:
                return True

            self.errors = self.content

            return False
        except Exception as e:
            self.errors = e
            logger.error(f'put failed. {e}')
        return False

    @property
    def reason(self):
        if 'reason' in dir(self.response):
            return self.response.reason

    @property
    def status_code(self):
        if 'status_code' in dir(self.response):
            return self.response.status_code

    @property
    def text(self):
        if self.response:
            return self.response.text

    async def to_dict(self):
        if self.response is not None:
            try:
                return json.loads(self.content)
            except Exception as error:
                logger.error(error)

    async def to_json(self):
        if self.content:
            try:
                return json.dumps(json.loads(self.content))
            except Exception as error:
                logger.error(error)

    async def update_headers(self, headers: dict):
        return self.session.headers.update(headers)


class Requests(RequestsClient):
    pass
