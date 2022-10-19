import re
import os
import json
import stat
import time
import psutil
import shutil
import requests

from queue import Queue
from bs4 import BeautifulSoup
from concurrent.futures import (ThreadPoolExecutor, wait, as_completed)

from automon.log.logger import Logging
from automon.helpers.subprocessWrapper import Run
from automon.helpers.sanitation import Sanitation

from .url import Url
from .file import File
from .options import Options
from .logstream import LogStream
from .config import YoutubeConfig

log_Youtube = Logging('Youtube', Logging.DEBUG)
logging_spaces = 0


class YoutubeClient(object):

    def __init__(self, max_thread_pool: int = None, urls_file: str = None, config: YoutubeConfig = None):
        """A multi-threaded wrapper for youtube-dl
        """

        self.config = config or YoutubeConfig()

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

        log_Youtube.debug(
            f'[finished ] {file.filename} ({os.stat(os.path.join(self.dir_downloading, file.filename)).st_size} B)')
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
