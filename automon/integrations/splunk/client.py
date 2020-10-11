import datetime

import splunklib.results
import splunklib.client as client

from queue import Queue

from automon.log import Logging
from automon.integrations.splunk.config import SplunkConfig


class JobError:
    _log = Logging('JobError', level=Logging.DEBUG)

    def __init__(self, job: client.Job):
        self._job = job

        self.messages = job.content['messages']
        try:
            self.fatal = self.messages['fatal']
            self.error = self.messages['error']

            self._log.critical(self.fatal)
            self._log.error(self.error)
        except:
            pass


class Job:
    _log = Logging('Job', level=Logging.DEBUG)

    def __init__(self, job: client.Job):
        self._job = job

        try:
            self.sid = job['sid']
            self.isDone = job["isDone"]
            self.doneProgress = float(job["doneProgress"]) * 100
            self.scanCount = int(job["scanCount"])
            self.eventCount = int(job["eventCount"])
            self.resultCount = int(job["resultCount"])
            self._searchProviders = job.content['searchProviders']
            self._search = job.content['search'] if 'search' in job.content.keys() else None
            self._runDuration = job.content['runDuration'] if 'runDuration' in job.content.keys() else None
            self._pid = job.content['pid'] if 'pid' in job.content.keys() else None
            self._normalizedSearch = job.content[
                'normalizedSearch'] if 'normalizedSearch' in job.content.keys() else None
            self._earliestTime = job.content['earliestTime']
            self._cursorTime = job.content['cursorTime']
            self._diskUsage = job.content['diskUsage']

            self.error = JobError(job)
        except:
            pass

    def is_ready(self):
        return self._job.is_ready()

    def results(self):
        return self._job.results()

    def access(self):
        return self._job.access

    def content(self):
        return self._job.content

    def __str__(self):
        return f'{self._search} {self._searchProviders} ({self._runDuration} s) ({self._diskUsage} B)'


class SplunkRestClient:
    _log = Logging('SplunkRestClient', level=Logging.DEBUG)

    def __int__(self, config: SplunkConfig = SplunkConfig()):

        self.config = config


class SplunkClient:
    _log = Logging('SplunkClient', level=Logging.DEBUG)

    def __init__(self, config: SplunkConfig = SplunkConfig()):

        self.config = config
        try:
            self.client = client.connect(
                host=self.config.host,
                port=self.config.port,
                username=self.config.username,
                password=self.config.password,
                verify=self.config.verify,
                scheme=self.config.scheme,
                app=None,
                owner=None,
                token=None,
                cookie=None
            )

            # referred to as a service in docs
            self.service = self.client
            assert isinstance(self.service, client.Service)

        except Exception as e:
            self.client = False

        self.queue = Queue()

    def info(self):
        return f'{self}'

    def search(self, query):
        """create normal search query"""
        kwargs_normalsearch = {"exec_mode": "normal"}
        job = self.create_job(query, **kwargs_normalsearch)
        # job = self.create_job(query)
        return self.results(job)

    def oneshot(self, query, earliest_time: str = '-15m', latest_time: str = 'now'):
        """create oneshot search"""
        kwargs_oneshot = {
            "earliest_time": earliest_time,
            "latest_time": latest_time
        }
        searchquery_oneshot = query
        oneshotsearch_results = self.service.jobs.oneshot(searchquery_oneshot, **kwargs_oneshot)
        reader = splunklib.results.ResultsReader(oneshotsearch_results)

        return [x for x in reader]

    def query(self, query):
        return self.search(query)

    def jobs(self):
        """get collection of search jobs"""
        return self.service.jobs

    def create_job(self, query, **kwargs):
        """create search job"""
        return self.service.jobs.create(query, **kwargs)

    def results(self, job: client.Job):
        """io blocking waiting for job results"""
        j = Job(job)
        while True:
            while not j.is_ready():
                pass
            if j.isDone == '1':
                break

        results = [x for x in splunklib.results.ResultsReader(j.results())]
        return results

    def job_summary(self):
        return f'There are {len(self.jobs())} jobs available to the current user'

    def get_apps(self):
        return [Application(x) for x in self.service.apps]

    def create_app(self, app_name):
        return self.apps.create(app_name)

    def get_app(self, app_name):
        return self.apps[app_name]

    def delete_app(self, app_name):
        return self.apps.delete(app_name)

    def app_info(self, app_name):
        return f'{self.service.apps[app_name]}'

    def __str__(self):
        if self.client:
            return f'connected to {self.config}'
        return f'not connected to {self.config}'


class Application:
    def __init__(self, object):
        self._app = object

        self.access = object['access']
        self.content = object['content']
        self.defaults = object['defaults']
        self.fields = object['fields']
        self.links = object['links']
        self.name = object['name']
        self.path = object['path']
        self.service = object['service']
        self.setupInfo = object['setupInfo']
        self.state = object['state']

        self._state = object['_state']
