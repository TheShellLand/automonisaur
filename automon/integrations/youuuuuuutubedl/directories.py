import os

from automon.log import Logging

log = Logging('Directories', level=Logging.DEBUG)


class Directories:
    downloading: str = os.path.join('youuuuuuutubedl', 'downloading')
    finished: str = os.path.join('youuuuuuutubedl', 'finished')
    pending: str = os.path.join('youuuuuuutubedl', 'pending')
    cookies: str = os.path.join('youuuuuuutubedl', 'cookies')

    def __init__(self):
        self.downloading = os.path.join('youuuuuuutubedl', 'downloading')
        self.finished = os.path.join('youuuuuuutubedl', 'finished')
        self.pending = os.path.join('youuuuuuutubedl', 'pending')
        self.cookies = os.path.join('youuuuuuutubedl', 'cookies')

    def __repr__(self):
        return f'{self.__dict__}'

    @property
    def isReady(self):
        for dir in [self.downloading, self.finished, self.pending, self.cookies]:
            if not os.path.exists(dir):
                return False
        return True

    def prepare_folders(self):
        dirs = [self.downloading, self.finished, self.pending, self.cookies]

        for directory in dirs:
            if not os.path.exists(directory):
                os.makedirs(directory)
                log.debug(f'makedir {directory}')
            if directory == self.downloading:
                for directory in os.listdir(self.downloading):
                    # Don't delete up previous downloads
                    # Clean out previous downloads
                    # os.remove(self.dir_d + '/' + directory)
                    pass
