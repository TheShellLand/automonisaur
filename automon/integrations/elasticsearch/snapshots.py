import json
import logging
import requests

logging.basicConfig(level=logging.INFO)


class Snapshot:
    def __init__(self, snapshot):
        self.snapshot = snapshot
        self.id = snapshot['id']
        self.status = snapshot['status']
        self.start_epoch = snapshot['start_epoch']
        self.start_time = snapshot['start_time']
        self.end_epoch = snapshot['end_epoch']
        self.end_time = snapshot['end_time']
        self.duration = snapshot['duration']
        self.indices = snapshot['indices']
        self.successful_shards = snapshot['successful_shards']
        self.failed_shards = snapshot['failed_shards']
        self.total_shards = snapshot['total_shards']

    def __eq__(self, other):
        if not isinstance(other, Snapshot):
            return NotImplemented

        return self.snapshot == other.snapshot


class ElasticsearchSnapshotMonitor:
    def __init__(self, elasticsearch_endpoint, elasticsearch_repository, snapshots_prefix):

        self.endpoint = elasticsearch_endpoint
        self.repository = elasticsearch_repository
        self.snapshots_prefix = snapshots_prefix
        self.url = '{endpoint}/_cat/snapshots/{repository}?format=json&pretty'.format(
            endpoint=self.endpoint, repository=self.repository) if self.endpoint else None

        self.snapshots = []
        self.total_snapshots = None
        self.good_snapshots = []
        self.bad_snapshots = []
        self.error = None

    def _get_all_snapshots(self):
        logging.info('Downloading snapshots list')

        url = self.url

        request = requests.get(url)
        content = request.content

        logging.info('\tStatus code: {}'.format(request.status_code))

        json_snapshots = json.loads(content)
        self._process_snapshots(json_snapshots)

    def _process_snapshots(self, snapshots):
        logging.info('Processing snapshots')

        try:
            self.total_snapshots = list(snapshots).__len__()

            logging.info('{} snapshots'.format(self.total_snapshots))
            for snapshot in snapshots:

                s = Snapshot(snapshot)

                id = s.id
                status = s.status

                if self.snapshots_prefix in id:

                    self.snapshots.append(s)

                    if status == 'SUCCESS' or status == 'success':
                        self.good_snapshots.append(s)
                    else:
                        self.bad_snapshots.append(s)
        except:
            logging.error('Unable to get snapshots')
            self.error = SnapshotError(snapshots)

    def read_file(self, file_path):
        logging.info('Reading snapshots from file')

        with open(file_path, 'rb') as snapshots:
            snapshots = json.load(snapshots)

        self._process_snapshots(snapshots)

    def check_snapshots(self):
        logging.info('Checking snapshots')
        self._get_all_snapshots()


class ElasticsearchSnapshotMonitorDepreciated:
    def __init__(self, elasticsearch_endpoint, elasticsearch_repository, snapshots_prefix):

        self.endpoint = elasticsearch_endpoint
        self.repository = elasticsearch_repository
        self.snapshots_prefix = snapshots_prefix
        self.snapshots = []
        self.good_snapshots = []
        self.bad_snapshots = []

    def _get_all_snapshots(self, file=None):
        url = '{endpoint}/_cat/snapshots/{repository}?format=json&pretty'.format(
            endpoint=self.endpoint, repository=self.repository)

        if file:
            with open(file, 'rb') as snapshots:
                snapshots = json.load(snapshots)
        else:
            snapshots = requests.get(url).content
            snapshots = json.loads(snapshots)

        for snapshot in snapshots:

            s = Snapshot(snapshot)
            id = s.id
            status = s.status

            if self.snapshots_prefix in id:

                self.snapshots.append(s)

                if status == 'SUCCESS' or status == 'success':
                    self.good_snapshots.append(s)
                else:
                    self.bad_snapshots.append(s)

    def read_file(self, file):
        self._get_all_snapshots(file)

    def check_snapshots(self):
        self._get_all_snapshots()


class SnapshotError:
    def __init__(self, error):
        self.error = error['error']
        self.root_cause = self.error['root_cause']
        self.type = self.error['type']
        self.reason = self.error['reason']
        self.cause_by_type = self.error['caused_by']['type']
        self.cause_by_reason = self.error['caused_by']['reason']
        self.cause_by_type_nested = self.error['caused_by']['caused_by']['type']
        self.cause_by_reason_nested = self.error['caused_by']['caused_by']['reason']
        self.status = error['status']

    def __eq__(self, other):
        if not isinstance(other, SnapshotError):
            return NotImplemented

        return self.error == other.error
