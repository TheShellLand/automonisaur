import re
import os
import json
import stat
import time
import psutil
import shutil
import requests
import subprocess

from queue import Queue
from shutil import move
from subprocess import PIPE
from bs4 import BeautifulSoup
from concurrent.futures import (ThreadPoolExecutor, wait, as_completed)

from automon.log.logger import Logging
from automon.helpers.subprocessWrapper import Run
from automon.helpers.sanitation import Sanitation

# logging
log_Url = Logging('Url', Logging.DEBUG)
log_Options = Logging('Options', Logging.DEBUG)
log_LogStream = Logging('LogStream', Logging.ERROR)
log_File = Logging('File', Logging.ERROR)
log_Youtube = Logging('Youtube', Logging.DEBUG)

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

        self.url = url
        self.name = name if name else ''
        self.folder = folder if folder else ''

        self.custom_name = self.name
        self.custom_folder = self.folder

        self.files = []

        log_Url.debug(f'{self.__str__()}')

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


class LogStream(object):
    def __init__(self):
        """Hold a bunch of logs
        """
        self.logs = []
        self.errors = []

    def store(self, log):
        """Logs are expected as a string list
        """
        output, error = log

        output = output.decode().splitlines()
        error = error.decode().splitlines()

        self.logs.extend(output)
        self.errors.extend(error)

        log_LogStream.debug(f'{len(self.logs)} lines')
        if self.errors:
            if len(self.errors) > 5:
                log_LogStream.error(f'{len(self.errors)} lines')
            else:
                log_LogStream.error(f'{self.errors}')

    def pop(self, index=0):
        """Pop a log off the top
        """
        try:
            log = self.logs.pop(index)
            log_LogStream.debug(log)
            return log
        except:
            return False


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


class Youtube(object):

    def __init__(self, max_thread_pool: int = None, urls_file: str = None):
        """A multi-threaded wrapper for youtube-dl
        """

        # Directories
        self.dir_downloading = os.path.join('files', 'downloading')
        self.dir_finished = os.path.join('files', 'finished')
        self.dir_pending = os.path.join('files', 'pending')
        self.dir_cookies = os.path.join('files', 'cookies')

        self._prepare_folders()

        self.run = Run()
        self.urls_file = urls_file
        self.urls = self._url_builder()
        self.cookies = self._cookie_builder(self.dir_cookies) or []

        self.downloads = []
        self.downloading = []
        self.finished = []

        self.thread_pool = self._config_thread_pool(thread_pool=max_thread_pool)
        self.queue = Queue()

        self._queue_urls()
        self._start_downloads(mp3=False)

    def _config_thread_pool(self, thread_pool):
        """Configure threading pool
        """

        if thread_pool:
            return ThreadPoolExecutor(max_workers=thread_pool)
        else:
            if self.urls:
                return ThreadPoolExecutor(len(self.urls))
            else:
                return ThreadPoolExecutor()

        return False

    def _cookie_builder(self, cookies):
        """Create a clean list of cookies
        """

        cookies = self._cookie_jar(cookies)

        return cookies

    def _cookie_jar(self, cookie_path):
        """Create a list of cookies
        """

        temp_c = []
        cookies = []
        # Open cookies
        # Cookies exported from Google Chrome extension 'EditThisCookie'
        for _ in os.listdir(cookie_path):
            with open(cookie_path + '/' + _, 'r') as f:
                cookie = f.read()
                temp_c.append(cookie)

        for _ in temp_c:
            # TODO: bug - self._cookie_jar() should return ready-to-use cookie objects built by requests.cookies
            cookie = json.loads(_)  # list of dicts

            # TODO: bug - requests.cookies.RequestsCookieJar() is broken
            # jar = requests.cookies.RequestsCookieJar()

            if len(cookie) > 1:
                for _ in cookie:
                    # TODO: bug - build cookie object with requests
                    pass

        return cookies

    def _download(self, url_object: Url, yt: Options):
        """Download the url
        """

        start = int(time.time())

        url = url_object.url
        name = url_object.custom_name
        folder = url_object.custom_folder

        if yt.mp3:
            file = File(url=url, filename=name, folder=folder, extension='.mp3')
        else:
            file = File(url=url, filename=name, folder=folder)

        logs = LogStream()

        # Download file
        log_Youtube.debug(f'[{"downloading": >{logging_spaces}}] {name}')
        self.downloads.append(file.add_logs(logs))
        logs.store(self._run(yt.dl))

        # get filename from logs
        file.get_filename(self.dir_downloading)

        self._finished(file)
        log_Youtube.info(f'[{"download": >{logging_spaces}}] took {int(time.time() - start)} seconds to complete {url}')

    def _finished(self, file: File):
        """Handle finished download
        """

        log_Youtube.debug(f'[finished ] {file.filename} ({os.stat(os.path.join(self.dir_downloading, file.filename)).st_size} B)')
        self._move_file(file)

    def _url_builder(self) -> [Url]:
        """Create a clean list of urls

        You can put any text file or html file into files/pending

        The list builder will take any file inside of files/pending
        and create a list of URLs from it
        """

        return self._read_files(self.dir_pending)

    def _read_files(self, directory) -> [Url]:
        """Read files from 'pending'
        """

        urls = []

        def html_file(f: str) -> [Url.url]:
            """Read HTML file
            """

            urls = []

            # Read with Beautifulsoup
            soup = BeautifulSoup(f.read(), 'html.parser')
            for a in soup.find_all('a', href=True):
                a = a['href'].strip()
                # TODO: bug - Need to append originating URL to <href> link
                if a == '' or a.startswith('#') or a.startswith('/'):
                    continue
                else:
                    urls.append(a)

            return urls

        def get_page(url: str) -> [Url.url]:
            """Download and parse the page
            """

            urls = []
            cookies = self.cookies

            def request_page(url):
                """Download the page

                Try using each cookie with every page
                """

                urls = []

                # TODO: feat - Add URL regex
                r = ''

                # TODO: feat - Make downloading multithreaded
                # Run a new thread for each cookie

                for _ in cookies:
                    jar = _
                    # TODO: feat - Add logic to only use cookie if url is in cookie['domain']
                    # If url is in cookie, use cookie
                    r = requests.get(url, cookies=jar)
                    soup = BeautifulSoup(r.text, 'html.parser')
                    for a in soup.find_all('a', href=True):
                        a = a['href'].strip()
                        url = url + a
                        # TODO: bug - Assert string is a URL
                        # if re.findall(r, _):
                        urls.append(url)

                return urls

            for page_urls in request_page(url):
                urls.extend(page_urls)

            return urls

        for item in os.listdir(directory):
            file_ = os.path.join(directory, item)

            log_Youtube.debug(f'[{"reading": >{logging_spaces}}] {file_}')

            if os.path.isfile(file_):

                fn, fext = os.path.splitext(item)

                # ignore hidden files
                if not fn.startswith('.') and not fn.startswith('#'):

                    with open(file_, 'r') as f:
                        if 'html' in fext.lower() or 'htm' in fext.lower():  # HTML file
                            urls.extend(html_file(f))

                        else:
                            for line in f.read().splitlines():  # Regular text file
                                if line == '' or line.startswith('#') or line.startswith('/'):
                                    continue

                                url_object = self._prepare_url(line)

                                if url_object in urls:
                                    continue

                                if 'youtube.com' in url_object.url.lower():
                                    urls.append(url_object)
                                elif url_object.url:
                                    urls.append(url_object)
                                else:
                                    # TODO: bug - Determine whether to parse the page or not
                                    # If the page needs to be parsed for URLs, parse it
                                    # If the page doesn't need to be parsed for URLS, append it

                                    # for _ in get_page(url):
                                    #     urls.append(_)
                                    urls.append(url_object)
        return urls

    def _run(self, command):
        """Run a command
        """
        try:
            log_Youtube.debug(f'[{"run": >{logging_spaces}}] {command}')
            return self.run.run_command(command)
            # return subprocess.Popen(command.split(), stdout=PIPE, stderr=PIPE).communicate()
        except Exception as e:
            log_Youtube.error(e)

    def _start_downloads(self, mp3: bool = True):
        """Start downloads in thread pool
        """
        downloads = 0
        sleep = 0
        while True:
            if self.queue.empty():
                break

            if self._max_cpu_usage(80):
                url = self.queue.get()
                downloads += 1

                # download video
                video_options = Options(folder=self.dir_downloading, url_object=url)
                self.futures.append(self.thread_pool.submit(self._download, url, video_options))

                if mp3:
                    # download mp3
                    mp3_options = Options(folder=self.dir_downloading, url_object=url, mp3=True)
                    self.futures.append(self.thread_pool.submit(self._download, url, mp3_options))
                    log_Youtube.info(f'[{"download": >{logging_spaces}}] ({downloads}/{len(self.urls)}) {url}')
                    sleep = int(sleep / 2)
            else:
                sleep += int(sleep + 1 * 2)
                # self._log.debug('[_downloader] Sleeping for: {} seconds'.format(sleep))
                time.sleep(sleep)

    def _max_cpu_usage(self, max_cpu_percentage=80):
        """Limit max cpu usage
        """
        if psutil.cpu_percent() < max_cpu_percentage:
            log_Youtube.debug(f'[{"cpu": >{logging_spaces}}] {psutil.cpu_percent()}%')
            return True
        else:
            log_Youtube.debug(f'[{"cpu": >{logging_spaces}}] {psutil.cpu_percent()}%')
            return False

    def _move_file(self, file: File):
        """Move file
        """

        filename = file.filename
        folder = file.folder

        source = os.path.join(self.dir_downloading, filename)

        if not os.path.exists(source):
            log_Youtube.error(f'[move ] source not found: {source}')
            return False

        if folder:
            if not os.path.exists(os.path.join(self.dir_finished, folder)):
                os.mkdir(os.path.join(self.dir_finished, folder))
            destination = os.path.join(self.dir_finished, folder, filename)
            destination_short = f'{os.path.split(os.path.split(destination)[0])[1]}/{os.path.split(destination)[1]}'
        else:
            destination = os.path.join(self.dir_finished, filename)
            destination_short = f'{os.path.split(os.path.split(destination)[0])[1]}/{os.path.split(destination)[1]}'

        try:
            log_Youtube.debug(f'[moving ] {os.path.split(destination)[-1]} ({os.stat(source).st_size} B)')

            # copy content, stat-info (mode too), timestamps...
            shutil.copy2(source, destination)
            # copy owner and group
            st = os.stat(source)
            os.chown(destination, st[stat.ST_UID], st[stat.ST_GID])
            # os.remove(source)

            log_Youtube.debug(
                f'[moved ] {destination_short} ({os.stat(destination).st_size} B)')
            return True
        except Exception as e:
            log_Youtube.error(f'[moving ] failed {os.path.split(source)[-1]}')
            return False

    def _prepare_folders(self):
        _dirs = [self.dir_downloading, self.dir_finished, self.dir_pending, self.dir_cookies]

        for directory in _dirs:
            if not os.path.exists(directory):
                os.makedirs(directory)
            if directory == self.dir_downloading:
                for directory in os.listdir(self.dir_downloading):
                    # Don't delete up previous downloads
                    # Clean out previous downloads
                    # os.remove(self.dir_d + '/' + directory)
                    pass

    def _prepare_url(self, raw_url: str) -> tuple:

        if not isinstance(raw_url, str) and not raw_url:
            return False

        regex = {
            'all': f'(.*),(.*),(.*)',
            'no folder': f'(.*),(.*)',
            'url only': f'(.*)'
        }

        for s, r in regex.items():
            result = re.search(r, raw_url)

            if result:
                if s == 'all':
                    url, name, folder = result.groups()

                if s == 'no folder':
                    url, name = result.groups()
                    folder = ''

                if s == 'url only':
                    url = result.groups()[0]
                    name = ''
                    folder = ''

                break

        url = Sanitation.strip(url)
        name = Sanitation.safe_filename(name)
        folder = Sanitation.safe_foldername(folder)

        return Url(url, name, folder)

    def _queue_urls(self):
        """Add urls to queue
        """
        added = 0
        urls = len(self.urls)
        self.futures = list()
        for url in self.urls:
            added += 1
            self.queue.put(url)
            log_Youtube.info(f'[{"queue": >{logging_spaces}}] ({added}/{urls}) {url}')


def main():
    """Main

    """
    Youtube()


if __name__ == '__main__':
    main()
