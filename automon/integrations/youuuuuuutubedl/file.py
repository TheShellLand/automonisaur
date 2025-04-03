import re
import os

from automon.log.logger import Logging

from .logstream import LogStream

log_File = Logging('File', Logging.ERROR)
logging_spaces = 0


class File(object):
    def __init__(self, url: str, filename: str, folder: str = None, extension: str = None):

        self.url = url
        self.download_name = filename
        self.folder = folder or ''
        self.extension = extension or ''
        self.filename = None
        self.size = None

        self.logs = LogStream()

    def add_logs(self, logs: LogStream):
        self.logs = logs

    def _parse_log(self, log: str):
        log_regexes = [
            # merging files into better format
            {'type': 'finished', 'regex': '(?<=Merging formats into ").*(?=")'},
            # file exists
            {'type': 'finished', 'regex': '(?<=^\[download\] ).*(?= has already been downloaded)(?= and merged)?'},
            # create new file
            {'type': 'finished', 'regex': '(?<=Merging formats into ").*(?=")'},
            # new audio file
            {'type': 'finished', 'regex': '(?<=Destination: ).*mp3'},
            # catch all files
            {'type': 'finished', 'regex': '(?<=Destination: ).*'},
        ]

        for r in log_regexes:
            regex = r.get('regex')
            r_type = r.get('type')

            m = re.search(regex, log)

            if m:
                log_File.debug(f'[regex] {regex} => {m.group()}')
                return m.group()

    def get_filename(self, download_path):

        while True:

            log = self.logs.pop()

            if log is False:
                break

            result = self._parse_log(log)

            if result:
                filename = os.path.split(result)[1]
                extension = os.path.splitext(filename)[1]
                filepath = os.path.join(download_path, filename)

                if os.path.exists(filepath):
                    self.filename = filename
                    if not self.extension:
                        self.extension = extension
                    self.size = os.stat(filepath).st_size
                    log_File.info(f'{self.filename}')

    def __str__(self):
        if self.download_name and self.extension and self.folder:
            return f'{self.folder}/{self.download_name}{self.extension}'
        elif self.download_name and self.folder:
            return f'{self.folder}/{self.download_name}'
        else:
            return f'{self.download_name}'

    def __eq__(self, other):
        if isinstance(other, File):
            return (self.download_name, self.extension, self.filetype) \
                   == (other.download_name, other.extension, other.filetype)
        else:
            return NotImplemented
