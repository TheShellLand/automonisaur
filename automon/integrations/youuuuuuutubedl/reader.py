import os

from .url import Url


class Reader(object):
    file: str
    urls: [Url]

    def __init__(self, file: str = None, directory: str = None):
        """Read a file. Make a list of URLs"""

        self.urls = []

        if directory:
            for f in self.read_directory(directory):
                self.urls.extend(self.read_file(file=f))

        if file:
            self.urls.extend(self.read_file(file))

    def read_directory(self, directory: str) -> [str]:
        """Read directory, return list of files"""
        return os.listdir(directory)

    def read_file(self, file: str) -> [Url]:
        """Read a file, return Urls

        Ignore lines starting with: '#'
        """
        urls = []

        with open(file, 'r') as f:
            lines = open(file, 'r')
            lines = lines.splitlines()

        for url in lines:
            if url == '' or url.startswith('#'):
                continue
            urls.append(Url(url=url))

        return urls
