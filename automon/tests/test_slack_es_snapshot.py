from automon.integrations.slack.slack import Slack
from automon.integrations.elasticsearch.config import ConfigESSnapshotBot


def test_es_snapshot_bot():
    conf = ConfigESSnapshotBot()
    Slack(username=conf.slack_name).alert('This is a JVM test')
