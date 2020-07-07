from automon.slack import Slack
from automon.config import ConfigESJVMBot


def test_es_jvm_bot():
    conf = ConfigESJVMBot()
    Slack(conf.slack_webhook, username=conf.slack_name).alert('This is a JVM test')
