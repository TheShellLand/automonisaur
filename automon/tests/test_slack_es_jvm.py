from automon.integrations.slack.slack import Slack
from automon.integrations.elasticsearch.config import ConfigESJVMBot


def test_es_jvm_bot():
    conf = ConfigESJVMBot()
    Slack(username=conf.slack_name).alert('This is a JVM test')
