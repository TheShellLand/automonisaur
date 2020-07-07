from automon.slack import Slack
from automon.config import ConfigESSnapshotBot


def test_es_snapshot_bot():
    conf = ConfigESSnapshotBot()
    Slack(conf.slack_webhook, username=conf.slack_name).alert('This is a JVM test')
