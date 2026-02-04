## DEMISTO MOCK CLASSES FOR LOCAL DEBUGGING
try:
    from local_dev.demistoWrapper import *
    from local_dev.demistoWrapper import __line__
    from local_dev.automon import *
    # from local_dev.common.debugging import *
    # from local_dev.common import *
    from integrations.proofpoint.threat_response_cloud.creds import *
except:
    pass

from automon.integrations.requestsWrapper import RequestsClient
from automon.helpers.dictWrapper import Dict

DEBUG = 1


def debug(log: str = '\n', level: int = 1, json_output: bool = False):
    if json_output:
        import json
        log = json.dumps(log)
    else:
        log = str(log)

    if level <= DEBUG:
        print(log)


class ProofpointThreatResponseCloudMessage(Dict):
    abuse_reporter_rank: str
    body_expired: str
    body_present: bool
    clear_confidence: str
    clear_verdict: str
    click_block_exclusive: bool
    created_at: str
    disposition: str
    email_id: str
    email_message_size: int
    email_recipient_id: str
    email_subject: str
    id: str
    incidents: list
    last_known_type: str
    message_id: str
    message_status: dict
    mime_content_expired: None
    mime_content_present: bool
    quarantine_strategy: str
    received_at: str
    received_time: str
    recipient_address: str
    remediation_status: str
    remediation_status_context: None
    sender_address: str
    sender_id: str
    sources: list
    tap_cleared: str
    tap_false_positive: bool
    tap_threat_types: list
    tenant_id: str
    updated_at: str
    vap: bool
    vip: bool

    def __init__(self):
        super().__init__()

        self.automon_body_mime: XsoarEmail = XsoarEmail()

    def __repr__(self):
        return (
            f'{self.created_at[:10]} :: '
            f'{self.automon_body_mime.__len__()} KB :: '
            f'{self.clear_verdict} :: '
            f'{self.clear_confidence} :: '
            f'{self.incidents.__len__()} incidents :: '
            f'{self.sender_address} -> '
            f'{self.recipient_address} :: '
            f'{self.email_subject}'
        )

    def __eq__(self, other):
        if isinstance(other, ProofpointThreatResponseCloudMessage):
            if self.message_id == other.message_id:
                return True
            return False
        raise Exception(f'Cannot compare {self} and {other}')

    def _enhance(self):
        self.incidents = [ProofpointThreatResponseCloudIncident().automon_update(x) for x in self.incidents]


class ProofpointThreatResponseCloudMessageResponse(Dict):
    endRow: int
    messages: list[ProofpointThreatResponseCloudMessage]
    statRow: int
    total: int

    def __init__(self):
        super().__init__()
        self.messages = []

    def __repr__(self):
        return f'{self.messages.__len__()} messages'

    def _enhance(self):
        self.messages = [ProofpointThreatResponseCloudMessage().automon_update(x) for x in self.messages]


class ProofpointThreatResponseCloudIncident(Dict):
    abuseSourceIds: list[str]
    assignedTeamId: str
    assignedTeamName: str
    clearConfidences: list[str]
    clearVerdicts: list[str]
    closedAt: str
    commentCount: int
    createdAt: str
    displayId: int
    dispositions: list[str]
    id: str
    messageCount: int
    sourceTypes: list[str]
    sourcesData: list[dict]
    state: str
    tenantId: str
    title: str
    updatedAt: str
    vap: bool
    vip: bool

    def __init__(self):
        super().__init__()

    def __repr__(self):
        return (
            f'{self.createdAt[:10]} :: '
            f'{self.state} :: '
            f'{self.messageCount} messages :: '
            f'{self.clearVerdicts} :: '
            f'{self.clearConfidences} :: '
            f'{self.dispositions} :: '
            f'{self.title}'
        )


class ProofpointThreatResponseCloudIncidentResponse(Dict):

    def __init__(self):
        super().__init__()
        self.incidents = []

    def __repr__(self):
        return f'{self.incidents.__len__()} incidents'

    def _enhance(self):
        self.incidents = [ProofpointThreatResponseCloudIncident().automon_update(x) for x in self.incidents]


class ProofpointThreatResponseCloudApi(object):
    version: str = 'v1'
    endpoint: str = 'https://threatprotection.proofpoint.com'
    endpoint_auth: str = 'https://auth.proofpoint.com'

    class Auth:
        @property
        def token(self) -> str:
            return f'/{ProofpointThreatResponseCloudApi.version}/token'

    class Incidents:

        @property
        def incidents(self):
            return f'/api/v1/tric/incidents'

        @property
        def create(self):
            return self.incidents + '/createIncident'

        @property
        def count(self):
            return self.incidents + '/count'

        def details(self, id: str):
            return self.incidents + f'/{id}'

        def details_all(self, id):
            return self.incidents + f'/{id}/messages'

        @property
        def summary(self):
            return self.incidents

        @property
        def upload_message(self):
            return self.incidents + '/uploadMessage'

    class Filters(Dict):
        """Filter that both incidents and messages use"""

        def __init__(self):
            """
            Message ID
                message_id_filters
                    RFC Message ID (including angular quotes <>)

            Remediation Status
                quarantine_filters
                    quarantine_mailbox_not_found
                    quarantine_message_not_found
                    quarantine_success
                    dl_resolved
                    quarantine_not_attempted
                    quarantine_pending

                    quarantine_skipped_skip_list
                    quarantine_skipped_abuse_mailbox
                    quarantine_skipped_no_server_for_mailbox
                    quarantine_skipped_cancelled

                    quarantine_failed_insufficient_permissions
                    quarantine_failed_invalid_authentication
                    quarantine_failed_invalid_license_for_mailbox
                    quarantine_failed_invalid_quarantine_folder
                    quarantine_failed_invalid_quarantine_mailbox
                    quarantine_failed_missing_message_id
                    quarantine_failed_no_connectivity
                    quarantine_failed_no_server_found_for_mailbox
                    quarantine_failed_throttled
                    quarantine_failed_other


                    restore_not_in_quarantine_mailbox
                    restore_pending
                    restore_success

                    restore_skipped_server_disabled
                    restore_skipped_server_unavailable

                    restore_failed_insufficient_permissions
                    restore_failed_invalid_authentication
                    restore_failed_invalid_license_for_mailbox
                    restore_failed_invalid_quarantine_folder
                    restore_failed_invalid_quarantine_mailbox
                    restore_failed_no_connectivity
                    restore_failed_no_server_found_for_mailbox
                    restore_failed_throttled
                    restore_failed_other

            Disposition
                disposition_filters
                    bulk
                    clean
                    impostor
                    in_progress
                    internal
                    low_risk
                    malware
                    manual_review
                    not_set
                    phish
                    scam
                    simulated_phish
                    spam
                    suspicious
                    tap_false_positive
                    toad
                    vendor

            TAP Threat ID
                tap_threat_filters
                    Threat ID from TAP

            TAP Threat Type
                tap_threat_type_filters
                    tap_threat_type_delivered_attachment_threat
                    tap_threat_type_delivered_message_threat
                    tap_threat_type_delivered_url_threat
                    tap_threat_type_unprotected_url_threat
            """
            super().__init__()
            self.filter = {}

        def to_json(self):
            import json
            return json.dumps(self.filter)

        def filters_status_filters_delivered(self):
            self.filter['filters']['status_filters'].append('message_delivered')
            return self

        def filters_status_filters_unread(self):
            self.filter['filters']['status_filters'].append('message_unread')
            return self

        def filters_status_filters_read(self):
            self.filter['filters']['status_filters'].append('message_read')
            return self

        def filters_status_filters_permitted_click(self):
            self.filter['filters']['status_filters'].append('permitted_click')
            return self

        def filters_recipient_address_filters(self, email: str):
            self.filter['filters']['recipient_address_filters'].append(email)
            return self

        def filters_sender_address_filters(self, email: str):
            self.filter['filters']['sender_address_filters'].append(email)
            return self

        def filters_subject_filters(self, subject: str):
            self.filter['filters']['subject_filters'].append(subject)
            return self

        def filters_other_filters_reporter(self):
            self.filter['filters']['other_filters'].append('reporter')
            return self

        def startRow(self, row: int = 0):
            self.filter['startRow'] = row
            return self

        def endRow(self, row: int = 200):
            self.filter['endRow'] = row
            return self

        def sortParams(self, sort: str = 'desc', colId: str = 'received_time'):
            self.filter['sortParams'] = [dict(sort=sort, colId=colId)]
            return self

        def filters_source_filters_abuse_mailbox(self):
            self.filter['filters']['source_filters'].append('abuse_mailbox')
            return self

        def filters_source_filters_tap(self):
            self.filter['filters']['source_filters'].append('tap')
            return self

        def filters_source_filters_smart_search(self):
            self.filter['filters']['source_filters'].append('smart_search')
            return self

        def filters_source_filters_message_csv_upload(self):
            self.filter['filters']['source_filters'].append('message_csv_upload')
            return self

        def filters_time_range_filter_start(self, timestamp: str):
            """yyyy-mm-dd hh:mm:ss"""
            self.filter['filters']['time_range_filter']['start'] = timestamp
            return self

        def filters_time_range_filter_end(self, timestamp: str):
            """yyyy-mm-dd hh:mm:ss"""
            self.filter['filters']['time_range_filter']['end'] = timestamp
            return self

        def filters_verdict_filters_failed(self):
            self.filter['filters']['verdict_filters'].append('verdict_failed')
            return self

        def filters_verdict_filters_low_risk(self):
            self.filter['filters']['verdict_filters'].append('verdict_low_risk')
            return self

        def filters_verdict_filters_manual_review(self):
            self.filter['filters']['verdict_filters'].append('verdict_manual_review')
            return self

        def filters_verdict_filters_threat(self):
            self.filter['filters']['verdict_filters'].append('verdict_threat')
            return self

        def filters_confidence_filters_high(self):
            self.filter['filters']['confidence_filters'].append('confidence_high')
            return self

        def filters_confidence_filters_medium(self):
            self.filter['filters']['confidence_filters'].append('confidence_medium')
            return self

        def filters_confidence_filters_low(self):
            self.filter['filters']['confidence_filters'].append('confidence_low')
            return self

    class IncidentsFilter(Filters):
        """Filter for incidents api"""

        def __init__(self):
            """

            Incident ID
                incident_id_filters
                    Valid incident ID (For example, "583" for INC-583)

            Incident Priority
                priority_filters
                    high
                    medium
                    low

            Very Attacked Person (VAP)
            	other_filters
            	    vap

            Disposition
                disposition_filters
                    bulk
                    clean
                    impostor
                    in_progress
                    internal
                    low_risk
                    malware
                    manual_review
                    not_set
                    phish
                    scam
                    simulated_phish
                    spam
                    suspicious
                    tap_false_positive
                    toad
                    vendor

            """
            super().__init__()

            self.filter = {
                "startRow": 0,
                "endRow": 200,
                "sortParams": [
                    {
                        "sort": "desc",
                        "colId": "createdAt"
                    }
                ],
                "filters": {
                    "confidence_filters": [],
                    "other_filters": [],
                    "recipient_address_filters": [],
                    "sender_address_filters": [],
                    "source_filters": [],
                    "status_filters": [],
                    "subject_filters": [],
                    "time_range_filter": {},
                    "verdict_filters": [],
                }
            }

        def filters_state_open_incidents(self):
            self.filter['filters']['other_filters'].append('open_incidents')
            return self

        def filters_state_closed_incidents(self):
            self.filter['filters']['other_filters'].append('closed_incidents')
            return self

    class Messages:

        @property
        def messages(self):
            return f'/api/v1/tric/messages'

        def details(self, id: str):
            return self.messages + f'/{id}'

        def download_mime_body(self, id):
            return self.messages + f'/{id}/download'

        def fetch_body(self, id):
            return self.messages + f'/{id}/fetch'

        def fetch_status(self, id):
            return self.messages + f'/{id}/fetchStatus'

    class MessagesFilter(Filters):
        """Filter for messages api"""

        def __init__(self):
            """
            Message ID
                message_id_filters
                    RFC Message ID (including angular quotes <>)

            Remediation Status
                quarantine_filters
                    quarantine_mailbox_not_found
                    quarantine_message_not_found
                    quarantine_success
                    dl_resolved
                    quarantine_not_attempted
                    quarantine_pending

                    quarantine_skipped_skip_list
                    quarantine_skipped_abuse_mailbox
                    quarantine_skipped_no_server_for_mailbox
                    quarantine_skipped_cancelled

                    quarantine_failed_insufficient_permissions
                    quarantine_failed_invalid_authentication
                    quarantine_failed_invalid_license_for_mailbox
                    quarantine_failed_invalid_quarantine_folder
                    quarantine_failed_invalid_quarantine_mailbox
                    quarantine_failed_missing_message_id
                    quarantine_failed_no_connectivity
                    quarantine_failed_no_server_found_for_mailbox
                    quarantine_failed_throttled
                    quarantine_failed_other


                    restore_not_in_quarantine_mailbox
                    restore_pending
                    restore_success

                    restore_skipped_server_disabled
                    restore_skipped_server_unavailable

                    restore_failed_insufficient_permissions
                    restore_failed_invalid_authentication
                    restore_failed_invalid_license_for_mailbox
                    restore_failed_invalid_quarantine_folder
                    restore_failed_invalid_quarantine_mailbox
                    restore_failed_no_connectivity
                    restore_failed_no_server_found_for_mailbox
                    restore_failed_throttled
                    restore_failed_other

            Disposition
                disposition_filters
                    bulk
                    clean
                    impostor
                    in_progress
                    internal
                    low_risk
                    malware
                    manual_review
                    not_set
                    phish
                    scam
                    simulated_phish
                    spam
                    suspicious
                    tap_false_positive
                    toad
                    vendor

            TAP Threat ID
                tap_threat_filters
                    Threat ID from TAP

            TAP Threat Type
                tap_threat_type_filters
                    tap_threat_type_delivered_attachment_threat
                    tap_threat_type_delivered_message_threat
                    tap_threat_type_delivered_url_threat
                    tap_threat_type_unprotected_url_threat
            """
            super().__init__()

            self.filter = {
                "startRow": 0,
                "endRow": 200,
                "sortParams": [
                    {
                        "sort": "desc",
                        "colId": "received_time"
                    }
                ],
                "filters": {
                    "confidence_filters": [],
                    "other_filters": [],
                    "recipient_address_filters": [],
                    "sender_address_filters": [],
                    "source_filters": [],
                    "status_filters": [],
                    "subject_filters": [],
                    "time_range_filter": {},
                    "verdict_filters": [],
                }
            }


class ProofpointThreatResponseCloudConfig(Dict):

    def __init__(
            self,
            PROOFPOINT_CLOUD_HOST: str = None,
            PROOFPOINT_CLOUD_SP: str = None,
            PROOFPOINT_CLOUD_SECRET: str = None,
            PROOFPOINT_CERT_VERIFY: bool = False,

    ):
        super().__init__()

        self.PROOFPOINT_CLOUD_HOST = PROOFPOINT_CLOUD_HOST or AutomonDemisto().params('PROOFPOINT_CLOUD_HOST')
        self.PROOFPOINT_CLOUD_SP = PROOFPOINT_CLOUD_SP or AutomonDemisto().params('PROOFPOINT_CLOUD_SP')
        self.PROOFPOINT_CLOUD_SECRET = PROOFPOINT_CLOUD_SECRET or AutomonDemisto().params('PROOFPOINT_CLOUD_SECRET')
        self.PROOFPOINT_CERT_VERIFY = PROOFPOINT_CERT_VERIFY or AutomonDemisto().params('PROOFPOINT_CERT_VERIFY')

        self.token = None

        if self.PROOFPOINT_CLOUD_HOST:
            self.PROOFPOINT_CLOUD_HOST = self.PROOFPOINT_CLOUD_HOST.split('https://')[-1]
            self.PROOFPOINT_CLOUD_HOST = self.PROOFPOINT_CLOUD_HOST.replace('/', '')
            self.PROOFPOINT_CLOUD_HOST = self.PROOFPOINT_CLOUD_HOST.strip()
            self.PROOFPOINT_CLOUD_HOST = f'https://{self.PROOFPOINT_CLOUD_HOST}'

        if self.PROOFPOINT_CLOUD_SP:
            self.PROOFPOINT_CLOUD_SP = self.PROOFPOINT_CLOUD_SP.strip()

        if self.PROOFPOINT_CLOUD_SECRET:
            self.PROOFPOINT_CLOUD_SECRET = self.PROOFPOINT_CLOUD_SECRET.strip()

        if PROOFPOINT_CERT_VERIFY is not None:
            self.PROOFPOINT_CERT_VERIFY = PROOFPOINT_CERT_VERIFY

        if not self.PROOFPOINT_CLOUD_HOST or \
                not self.PROOFPOINT_CLOUD_SP or \
                not self.PROOFPOINT_CLOUD_SECRET:
            raise Exception(f"[ProofpointThreatResponseCloudConfig] :: ERROR :: {self}")

    def __bool__(self):
        if self.is_ready():
            return True
        return False

    def is_ready(self) -> bool:
        if self.PROOFPOINT_CLOUD_HOST and \
                self.PROOFPOINT_CLOUD_SP and \
                self.PROOFPOINT_CLOUD_SECRET:
            return True
        return False

    @property
    def headers(self):
        return {
            "Content-Type": "application/x-www-form-urlencoded",
        }

    @property
    def headers_authenticated(self):
        return {
            'Authorization': f'Bearer {self.token}'
        }


class RateLimiter:
    def __init__(self, rate_per_sec=None, rate_per_min=None, daily_limit=None):
        import threading
        import collections

        # RPS: Minimum delay between any two calls
        self.min_delay = 1.0 / rate_per_sec if rate_per_sec else (60.0 / rate_per_min if rate_per_min else 0)
        self.last_call = 0.0

        self.rpm_limit = rate_per_min
        self.daily_limit = daily_limit

        # Single log of all request timestamps (limited to 24h window)
        self.history = collections.deque()
        self.lock = threading.Lock()

    def _clean(self, now):
        """Prune timestamps older than the longest window (24h)."""
        day_ago = now - 86400
        while self.history and self.history[0] < day_ago:
            self.history.popleft()

    def wait(self):
        import time

        sleep_duration = 0.0

        with self.lock:
            now = time.monotonic()
            self._clean(now)

            # 1. DAILY WINDOW: The entire deque represents the last 24h
            if self.daily_limit and len(self.history) >= self.daily_limit:
                wait_h = (86400 - (now - self.history[0])) / 3600
                raise RuntimeError(f"Daily limit hit. Try again in {wait_h:.2f}h")

            # 2. MINUTE WINDOW: Look back 60s from 'now'
            if self.rpm_limit:
                minute_ago = now - 60
                # Efficiently find calls within the last minute
                recent_calls = [t for t in self.history if t > minute_ago]
                if len(recent_calls) >= self.rpm_limit:
                    # Calculate wait until the oldest call in this 60s window expires
                    sleep_duration = max(sleep_duration, 60 - (now - recent_calls[0]))

            # 3. RPS WINDOW: Per-call spacing
            elapsed = now - self.last_call
            if elapsed < self.min_delay:
                sleep_duration = max(sleep_duration, self.min_delay - elapsed)

            # Pre-reserve the slot before releasing the lock
            self.last_call = now + sleep_duration

        # --- Sleep outside the lock so other threads aren't blocked ---
        if sleep_duration > 0:
            debug(f'[RateLimiter] :: '
                  f'wait :: '
                  f'{elapsed=} :: '
                  f'{sleep_duration=} :: '
                  f'{len(self.history)}/{self.daily_limit} requests')
            time.sleep(sleep_duration)

        with self.lock:
            self.history.append(time.monotonic())


class ProofpointThreatResponseCloudClient(RequestsClient):
    _api = ProofpointThreatResponseCloudApi()

    _rate_per_minute: int = 10
    _rate_max_per_day: int = 1800

    _limiter: RateLimiter = RateLimiter(rate_per_min=_rate_per_minute, daily_limit=_rate_max_per_day)

    def __init__(self, config: ProofpointThreatResponseCloudConfig = None):

        self.config = config or ProofpointThreatResponseCloudConfig()
        self.host = self.config.PROOFPOINT_CLOUD_HOST
        self.requests = RequestsClient()

    def is_ready(self) -> bool:
        if self.config.is_ready():
            if self.get_auth_bearer_token():
                self.requests.headers = self.get_auth_headers()
                return True
        return False

    def _wait_for_rate_limit(self):
        ProofpointThreatResponseCloudClient._limiter.wait()
        import time
        time.sleep(1)

    def get_auth(self) -> dict:
        self._wait_for_rate_limit()

        url = self._api.endpoint_auth + self._api.Auth().token
        data = {
            'grant_type': 'client_credentials',
            'client_id': self.config.PROOFPOINT_CLOUD_SP,
            'client_secret': self.config.PROOFPOINT_CLOUD_SECRET,
        }

        response = self._requests_post(
            url=url,
            data=data,
            headers=self.config.headers,
        )

        return response.to_dict()

    def get_auth_bearer_token(self) -> str:
        return self.get_auth().get('access_token')

    def get_auth_headers(self) -> dict:
        self.config.token = self.get_auth().get('access_token')
        self.headers = self.config.headers_authenticated
        return self.headers

    def _requests_get(self, url: str, **kwargs) -> RequestsClient:
        self._wait_for_rate_limit()

        response = self.requests.get_self(
            url=url,
            verify=self.config.PROOFPOINT_CERT_VERIFY,
            **kwargs)

        if not response:
            raise Exception(f'[ProofpointThreatResponseCloudClient] :: GET :: ERROR :: {url} :: {response.errors}')

        return response

    def _requests_post(self, url: str, data: str | dict = None, json: str = None, **kwargs) -> RequestsClient:
        self._wait_for_rate_limit()

        response = self.requests.post_self(
            url=url,
            data=data,
            json=json,
            verify=self.config.PROOFPOINT_CERT_VERIFY,
            **kwargs)

        if not response:
            raise Exception(f'[ProofpointThreatResponseCloudClient] :: POST :: ERROR :: {url} :: {response.errors}')

        return response

    def test_module(self) -> ProofpointThreatResponseCloudMessageResponse:
        """runs command test-module"""
        url = self.host + self._api.Messages().messages

        response = self._requests_get(
            url=url
        )

        raise

    def incident_get(self, id: str) -> ProofpointThreatResponseCloudIncident:
        url = self.host + self._api.Incidents().details(id)

        payload = {
            "filters": {
                "time_range_filter": {"start": "2025-11-05 06:00:35", "end": "2025-11-05 06:38:35"},
                "other_filters": [],
                "source_filters": []
            },
            "endRow": 30,
            "sortParams": [{
                "sort": "desc",
                "colId": "received_time"
            }],
            "startRow": 0
        }

        self._requests_post(
            url=url,
            data=payload,
        ).to_dict()

        response = self._requests_get(
            url=url,
        ).to_dict()
        response = ProofpointThreatResponseCloudIncident().automon_update(response)

        return response

    def fetch_incidents(self) -> ProofpointThreatResponseCloudIncidentResponse:
        """runs command fetch-incidents"""

        url = self.host + self._api.Incidents().incidents

        filter = self._api.IncidentsFilter(
        ).filters_state_open_incidents()

        filter_json = filter.to_json()

        response = self._requests_post(
            url=url,
            data=filter_json,
        ).to_dict()
        response = ProofpointThreatResponseCloudIncidentResponse().automon_update(response)

        return response

    def fetch_messages(self) -> ProofpointThreatResponseCloudMessageResponse:
        """runs command TBD"""

        url = self.host + self._api.Messages().messages

        filter = self._api.MessagesFilter(
        ).filters_verdict_filters_threat()

        filter_json = filter.to_json()

        response = self._requests_post(
            url=url,
            data=filter_json,
        ).to_dict()
        response = ProofpointThreatResponseCloudMessageResponse().automon_update(response)

        return response

    def fetch_indicators(self):
        """runs command fetch-indicators"""
        raise

    def long_running_execution(self):
        """runs command long-running-execution"""
        raise

    def message_download(self, message: ProofpointThreatResponseCloudMessage) -> ProofpointThreatResponseCloudMessage:
        """downloads message full MIME"""

        url = self.host + self._api.Messages().download_mime_body(message.id)

        response = self._requests_get(url)
        message.automon_body_mime = XsoarEmail(response.content)

        return message


class Regex(Dict):
    def __init__(self):
        super().__init__()

    def domain(self):
        return '''^(?!.{254,})((?!-)[a-zA-Z0-9-]{1,63}(?<!-)\.)+[a-zA-Z]{2,}$'''

    def email(self):
        return '''(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])'''

    def ipv4(self):
        return '''^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'''

    def ipv6(self):
        return '''^fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}$'''


class Grok(Regex):

    def __init__(self):
        super().__init__()
        import re
        self._re = re

        re.search()
        re.findall()
        re.match()

        self.pattern: str = ''
        self.compile: re.compile = None

    def set_regex(self, pattern: str):
        import re
        self.pattern = pattern
        self.compile = re.compile(pattern)
        return self

    def search(self):
        if self.compile:
            return self.compile.search()

    def findall(self):
        if self.compile:
            return self.compile.findall()

    def match(self):
        if self.compile:
            return self.match()


class XsoarEmailHeader(Dict):
    def __init__(self, header: tuple[str, str] = None):
        super().__init__()

        self.key = None
        self.value = None

        if header:
            key, value = header
            self.key = key
            self.value = value

    def __repr__(self):
        return f'{self.key} :: {self.value}'

    def __eq__(self, other):
        return self.key == other.key and self.value == other.value

    def __bool__(self):
        return bool(self.key and self.value)

    def find(self, key: str):
        return self.key.lower() == key.lower()


class XsoarEmailPayload(Dict):
    headers: list[XsoarEmailHeader]
    payload: str

    def __init__(self, headers: list = [], payload: str = ''):
        super().__init__()

        self.headers: list[XsoarEmailHeader] = [XsoarEmailHeader(x) for x in headers]
        self.payload: str = payload

        if 'application/octet-stream' in self.content_type:
            import base64
            self.payload = base64.b64decode(self.payload.encode()).decode()

    def __repr__(self):
        return f'{self.content_type} :: {len(self.payload)} KB'

    def find_header(self, key: str) -> XsoarEmailHeader | None:
        for header in self.headers:
            if header.find(key):
                return header

    @property
    def content_type(self) -> str | None:
        header = self.find_header('Content-Type')
        if header:
            return header.value

    @property
    def content_description(self) -> str | None:
        header = self.find_header('Content-Description')
        if header:
            return header.value


class XsoarEmail(Dict):

    def __init__(self, mime: bytes = b''):
        super().__init__()
        self.mime: bytes = mime

        if mime:
            pass

        if len(self) > 1000:
            self.automon_payload_all
            pass

    def __repr__(self):
        return f'{self.__len__()} KB :: {self.email}'

    def __bool__(self):
        if self.mime:
            return True
        return False

    def __len__(self):
        return len(self.mime)

    @property
    def automon_email_from(self):
        return self.automon_headers_get('from')

    @property
    def automon_email_to(self):
        return self.automon_headers_get('to')

    @property
    def automon_email_subject(self):
        return self.automon_headers_get('subject')

    @property
    def automon_content_type(self):
        return self.automon_headers_get('content-type')

    @property
    def automon_content_language(self):
        return self.automon_headers_get('content-language')

    @property
    def automon_message_id(self):
        return self.automon_headers_get('message-id')

    @property
    def automon_headers(self) -> list[XsoarEmailHeader]:
        if hasattr(self.email, '_headers'):
            return [XsoarEmailHeader(x) for x in self.email._headers]
        return []

    def automon_headers_get(self, name: str) -> XsoarEmailHeader | None:
        for header in self.automon_headers:
            if header.find(name):
                return header

    @property
    def automon_payload(self) -> list:
        payload = []
        if hasattr(self.email, '_payload'):
            payload += self.email._payload
        return payload

    def _automon_payload_extract(self, message) -> list[XsoarEmailPayload]:
        payloads = []
        if hasattr(message, '_payload'):
            if hasattr(message, '_headers'):
                _headers = message._headers
                _payload = message._payload

                if type(_payload) is list:
                    for _payload_nested in _payload:
                        payloads += self._automon_payload_extract(_payload_nested)
                else:
                    payloads.append(XsoarEmailPayload(_headers, _payload))

            else:
                raise Exception(f'missing headers :: ERROR :: {message=}')
        return payloads

    @property
    def automon_payload_all(self) -> list[XsoarEmailPayload]:
        payloads = []
        for message in self.automon_payload:
            payloads += self._automon_payload_extract(message)
        return payloads

    @property
    def decoded(self) -> str:
        return self.mime.decode()

    @property
    def email(self):
        import email
        return email.message_from_bytes(self.mime)


def main():
    try:

        config = ProofpointThreatResponseCloudConfig(
            PROOFPOINT_CLOUD_HOST=PROOFPOINT_CLOUD_HOST,
            PROOFPOINT_CLOUD_SP=PROOFPOINT_CLOUD_SP,
            PROOFPOINT_CLOUD_SECRET=PROOFPOINT_CLOUD_SECRET,
            PROOFPOINT_CERT_VERIFY=PROOFPOINT_CERT_VERIFY,
        )
        client = ProofpointThreatResponseCloudClient(config)

        if client.is_ready():
            # client.test_module()
            # client.incident_get()
            # incidents = client.fetch_incidents()
            messages = client.fetch_messages()
            downloads = [client.message_download(x) for x in messages.messages[:5]]
            pass
    except Exception as error:
        raise Exception(error)

    client = ProofpointThreatResponseCloudClient()

    command = AutomonDemisto().command
    params = AutomonDemisto().params()

    if command == "test-module":
        return_results(client.test_module())
    if command == 'fetch-incidents':
        debug(f'[main] :: fetch-incidents :: {command=}')
        client.fetch_incidents()
    if command == 'fetch-indicators':
        debug(f'[main] :: fetch-incidents :: {command=}')
        client.fetch_indicators()
    else:
        illumio_commands = {
            "proofpoint-test-module": client.test_module,
        }
        if command in illumio_commands:
            args = demisto.args()
            remove_nulls_from_dictionary(trim_spaces_from_args(args))
            return_results(illumio_commands[command](args))
        else:
            raise NotImplementedError(f"Command {command} is not implemented")


if __name__ in ("__main__", "__builtin__", "builtins"):  # pragma: no cover
    main()

register_module_line('IllumioCore', 'end', __line__())
