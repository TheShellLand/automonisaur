import re

from swiftclient.service import SwiftService, SwiftError, ClientException

from automon.log import Logging


class SwiftItem(object):
    def __init__(self, item: dict):
        self._log = Logging(SwiftItem.__name__, Logging.DEBUG)
        self._item = item
        self._dict = item

        self.size = int(item.get('bytes', 0))
        self.name = item.get('name')
        self.hash = item.get('hash')
        self.etag = self.hash

        self.content_type = item.get('content_type', None)
        self.last_modified = item.get('last_modified')

        if self.content_type == 'application/directory':
            self._is_directory = True
            self._dir_marker = True
        else:
            self._is_directory = False
            self._dir_marker = False

    def is_directory(self):
        return self._is_directory

    def has_dir_marker(self):
        return self._dir_marker

    def data(self):
        return self._item

    def filter(self, regex: str) -> bool:
        regex = str(regex)
        if re.search(regex, self.name):
            return True
        else:
            return False

    def __repr__(self):
        return f'{self.name} [size: {self.size}] [etag: {self.etag}]'


class SwiftPage(SwiftService):
    def __init__(self, page: dict) -> SwiftService.list:
        self._log = Logging(SwiftPage.__name__, Logging.ERROR)

        self._page = page

        self.action = self._page.get('action')
        self.container = self._page.get('container')
        self.prefix = self._page.get('prefix')
        self.success = self._page.get('success')
        self.marker = self._page.get('marker')
        self.error = self._page.get('error')
        self.traceback = self._page.get('traceback')
        self.error_timestamp = self._page.get('error_timestamp')

        if self.error == ClientException:
            self._log.error(f'{SwiftPage.__name__} {self.success} {self.error}')

        if self.success:
            self.listing = self._page.get('listing')
            self._log.debug(f'{SwiftPage.__name__} {self.success} {self.listing}')
        else:
            self.listing = []

    def _dict(self):
        return {
            'action': self.action,
            'container': self.container,
            'prefix': self.prefix,
            'success': self.success,
            'marker': self.marker,
            'error': self.error,
            'traceback': self.traceback,
            'error_timestamp': self.error_timestamp,
            'listing': self.listing
        }

    def _error_handler(self):
        if not self.success and isinstance(self.error, Exception):
            self._log.error(f'{SwiftError(self._page)}')

    def list_gen(self) -> object or SwiftItem:
        if self.success:
            for LIST in self.listing:
                yield SwiftItem(LIST)
        else:
            self._error_handler()

    def __repr__(self):
        return f'{self._page}'


class SwiftList(SwiftService):
    def __init__(self, container: str) -> SwiftService.list:
        """
        always request a new SwiftService object
        see documentation
        """

        self._log = Logging(SwiftList.__name__, Logging.DEBUG)
        self.container = container

    def list_gen(self) -> object or SwiftPage:
        with SwiftService() as swift:
            try:
                list_parts_gen = swift.list(container=self.container)

                # TODO: need to check if gi_running is True when connected, or always False
                if list_parts_gen.gi_running:
                    for page in list_parts_gen:
                        if page["success"]:
                            yield SwiftPage(page)
                        else:
                            self._log.error(f'{page["error"]}')

            except Exception as e:
                self._log.error(f'page failed, {e}')
