import unittest

from automon.integrations.elasticsearch.snapshots import Snapshot, SnapshotError, ElasticsearchSnapshotMonitor


class SnapshotTest(unittest.TestCase):

    def test_Snapshot(self):
        self.assertTrue(Snapshot)
        self.assertTrue(Snapshot({}))
        self.assertEqual(Snapshot({}), Snapshot({}))
        self.assertNotEqual(Snapshot({}), None)

    def test_SnapshotError(self):
        error = {
            'error': {
                'test': 'test',
                'caused_by': {
                    'type': None,
                    'reason': None,
                    'caused_by': {
                        'type': None,
                        'reason': None
                    }
                }
            }
        }

        self.assertTrue(SnapshotError)
        self.assertTrue(SnapshotError({}))
        self.assertEqual(SnapshotError({}), SnapshotError({}))
        self.assertNotEqual(SnapshotError({}), None)
        self.assertTrue(SnapshotError(error))

    def test_ElasticsearchSnapshotMonitor(self):
        e = ElasticsearchSnapshotMonitor(elasticsearch_repository='found-snapshots')

        if e.connected:
            self.assertTrue(ElasticsearchSnapshotMonitor)
            self.assertTrue(e)
            self.assertTrue(e.check_snapshots())
        else:
            self.assertTrue(ElasticsearchSnapshotMonitor)
            self.assertTrue(e)
            self.assertFalse(e.check_snapshots())


if __name__ == '__main__':
    unittest.main()
