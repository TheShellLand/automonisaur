import re

from neo4j.work.result import Result

from automon.log.logger import Logging

log = Logging(name=__name__, level=Logging.DEBUG)


class Results(Result):
    def __init__(self, results):
        self._results = results

        try:
            self._summary = results._summary
            self.counters = self._summary.counters
            self.notifications = self._summary.notifications
            self.query = self._summary.query
            self.query_type = self._summary.query_type

            self.metadata = self._summary.metadata
            self.stats = self.metadata.get('stats', None)
        except Exception as e:
            log.error(e, enable_traceback=False)

    def __str__(self):
        try:
            return f'{self.stats}'
        except:
            return 'no nodes'
