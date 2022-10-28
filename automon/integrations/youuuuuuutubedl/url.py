from automon.log.logger import Logging

from automon.helpers.sanitation import Sanitation

log_Url = Logging('Url', Logging.DEBUG)
logging_spaces = 0


class Url(object):
    url = str
    name = str
    folder = str
    download_name = str

    custom_name = str
    custom_folder = str

    filetype = type

    def __init__(self, url: str, name: str, folder: str):

        self.url = self.sanatize(url)
        self.name = name or ''
        self.folder = folder or ''

        self.custom_name = self.name
        self.custom_folder = self.folder

        self.files = []

        log_Url.debug(f'{self.__str__()}')

    def sanatize(self, url: str) -> tuple:
        """Sanitize url"""
        return Sanitation.strip(url)

    def __repr__(self):
        if self.folder and self.name:
            return f'{self.folder} {self.name} {self.url}'
        if self.folder and not self.name:
            return f'{self.folder} {self.url}'
        if not self.folder and self.name:
            return f'{self.name} {self.url}'
        else:
            return f'{self.url}'

    def __eq__(self, other):
        if isinstance(other, Url):
            return (self.url, self.name, self.download_name, self.folder) == \
                   (other.url, self.name, self.download_name, self.folder)
        else:
            return False
