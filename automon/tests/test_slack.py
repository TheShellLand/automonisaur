from automon.integrations.slack.slack import Slack
from automon.integrations.slack.config import ConfigSlack


def test_slack_test_message():
    conf = ConfigSlack()
    Slack(webhook=conf.slack_webhook, username=conf.slack_name).alert('this is a slack test message')
