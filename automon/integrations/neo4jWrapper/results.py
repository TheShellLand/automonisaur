import re

from neo4j.work.summary import ResultSummary

from automon.log import logger

log = logger.logging.getLogger(__name__)
log.setLevel(logger.DEBUG)


class Results(ResultSummary):
    def __init__(self, results):
        self._results = results
        self.summary = results._summary

        if self.summary:
            self.counters = self.summary.counters
            self.notifications = self.summary.notifications
            self.query = self.summary.query
            self.query_type = self.summary.query_type
            self.metadata = self.summary.metadata

            if self.metadata:
                self.stats = self.metadata.get('stats', None)

    def __str__(self):
        return f'{self.__dict__}'
