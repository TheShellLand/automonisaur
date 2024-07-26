import os

from automon.log.logger import Logging

from .url import Url

log_Options = Logging('Options', Logging.DEBUG)
logging_spaces = 0


class Options(object):
    def __init__(self, folder: str, url_object: Url, mp3: bool = False):

        # Youtube-dl configuration
        self._yt = os.path.join('bin', 'youtube-dl')
        self._yt_name = f'--get-filename -o "{folder}/%(title)s.%(ext)s"'
        self._yt_args = f'-o "{folder}/%(title)s.%(ext)s"'

        self.python = 'python3'

        self.mp3 = mp3

        name = url_object.custom_name or ''
        url = url_object.url

        if not mp3:
            if name:
                self.dl = f'{self.python} {self._yt} -o "{os.path.join(folder, name)}.%(ext)s" {url}'
            else:
                self.dl = f'{self.python} {self._yt} -o "{folder}/%(title)s.%(ext)s" {url}'

        # Requires ffmpeg or avconv and ffprobe or avprobe
        # apt install ffmpeg avconv
        # apt install ffprobe avprobe
        if mp3:
            if name:
                self.dl = f'{self.python} {self._yt} -o "{os.path.join(folder, name)}.%(ext)s" ' \
                          f'--extract-audio --audio-format mp3 -k {url}'
            else:
                self.dl = f'{self.python} {self._yt} {self._yt_args} --extract-audio --audio-format mp3 -k {url}'

    def __str__(self):
        return f'{self.dl}'
