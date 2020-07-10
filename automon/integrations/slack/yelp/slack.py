# https://github.com/Yelp/elastalert/blob/master/elastalert/alerts.py

import json
import slack
import requests
import warnings
import logging

logging.basicConfig(level=logging.INFO)


class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, 'isoformat'):
            return obj.isoformat()
        else:
            return json.JSONEncoder.default(self, obj)


class RequestException(IOError):
    """There was an ambiguous exception that occurred while handling your
    request.
    """

    def __init__(self, *args, **kwargs):
        """Initialize RequestException with `request` and `response` objects."""
        response = kwargs.pop('response', None)
        self.response = response
        self.request = kwargs.pop('request', None)
        if (response is not None and not self.request and
            hasattr(response, 'request')):
            self.request = self.response.request
        super(RequestException, self).__init__(*args, **kwargs)


class Slack:
    def __init__(self, webhook, username='Automon Test Bot', channel='#test_alerts', token=None,
                 proxy=None, ignore_ssl_errors=False, ca_certs=None):

        self.slack_webhook_url = [webhook]
        self.slack_username_override = username
        self.slack_channel_override = [channel]
        self.token = token
        self.client = slack.WebClient(token=self.token)
        self.slack_proxy = proxy
        self.slack_ignore_ssl_errors = ignore_ssl_errors
        self.slack_ca_certs = ca_certs

        self.slack_msg_color = 'danger'
        self.slack_timeout = 10

    def alert(self, text):
        post = text

        # post to slack
        headers = {'content-type': 'application/json'}
        # set https proxy, if it was provided
        proxies = {'https': self.slack_proxy} if self.slack_proxy else None
        payload = {
            'username': self.slack_username_override,
            'text': post
        }

        for url in self.slack_webhook_url:
            for channel_override in self.slack_channel_override:
                try:
                    if self.slack_ca_certs:
                        verify = self.slack_ca_certs
                    else:
                        verify = self.slack_ignore_ssl_errors
                    if self.slack_ignore_ssl_errors:
                        requests.packages.urllib3.disable_warnings()
                    payload['channel'] = channel_override
                    response = requests.post(
                        url, data=json.dumps(payload, cls=DateTimeEncoder),
                        headers=headers, verify=verify,
                        proxies=proxies,
                        timeout=self.slack_timeout)
                    warnings.resetwarnings()
                    response.raise_for_status()

                    logging.info('Slack message sent')

                except RequestException as e:
                    logging.error('Error posting to slack: %s' % e)
