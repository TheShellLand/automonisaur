import splunklib.client as client

from automon.log import Logging

log = Logging(name=__name__, level=Logging.DEBUG)


class JobError:

    def __init__(self, job: client.Job):
        self._log = Logging(JobError.__name__, level=Logging.DEBUG)
        self._job = job

        self.messages = job.content['messages']
        try:
            self.fatal = self.messages['fatal']
            self.error = self.messages['error']

            self._log.critical(self.fatal)
            self._log.error(self.error)
        except Exception as e:
            self._log.error(e)


class Job:

    def __init__(self, job: client.Job):
        self._log = Logging(Job.__name__, level=Logging.DEBUG)
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
        except Exception as e:
            self._log.error(e)

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


class Application:
    def __init__(self, app: dict):
        self._app = app

        self.access = app['access']
        self.content = app['content']
        self.defaults = app['defaults']
        self.fields = app['fields']
        self.links = app['links']
        self.name = app['name']
        self.path = app['path']
        self.service = app['service']
        self.setupInfo = app['setupInfo']
        self.state = app['state']

        self._state = app['_state']
