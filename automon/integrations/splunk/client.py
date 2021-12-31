from queue import Queue

import splunklib.results
import splunklib.client as client

from automon.log import Logging
from automon.integrations.splunk.config import SplunkConfig
from automon.integrations.splunk.helpers import Job, Application

log = Logging(name=__name__, level=Logging.DEBUG)


class SplunkRestClient:

    def __int__(self, config: SplunkConfig = SplunkConfig()):
        self._log = Logging(SplunkRestClient.__name__, level=Logging.DEBUG)
        self.config = config


class SplunkClient(object):

    def __init__(self, config: SplunkConfig = None):
        self._log = Logging(SplunkClient.__name__, level=Logging.DEBUG)
        self.config = config or SplunkConfig()

        try:
            self.client = client.connect(
                host=self.config.host,
                port=self.config.port,
                username=self.config.username,
                password=self.config.password,
                verify=self.config.verify,
                scheme=self.config.scheme,
                app=self.config.app,
                owner=self.config.owner,
                token=self.config.token,
                cookie=self.config.cookie,
                handler=self.config.handler
            )

            # referred to as a service in docs
            self.service = self.client
            self.connected = True
            assert isinstance(self.service, client.Service)

        except Exception as e:
            self.connected = False
            self._log.error(f'{e}\t{self.config.host}:{self.config.port}', enable_traceback=False)

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

    @staticmethod
    def results(job: client.Job):
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
        return self.service.apps.create(app_name)

    def get_app(self, app_name):
        return self.service.apps[app_name]

    def delete_app(self, app_name):
        return self.service.apps.delete(app_name)

    def app_info(self, app_name):
        return f'{self.service.apps[app_name]}'

    def __str__(self):
        if self.connected:
            return f'connected to {self.config}'
        return f'not connected to {self.config}'
