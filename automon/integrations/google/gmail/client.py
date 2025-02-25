import googleapiclient.discovery

from automon.helpers.loggingWrapper import LoggingClient, DEBUG
from automon.integrations.requestsWrapper import RequestsClient

from .config import GoogleGmailConfig
from .v1 import *

logger = LoggingClient.logging.getLogger(__name__)
logger.setLevel(DEBUG)


class GoogleGmailClient:
    """Google Gmail client

    https://developers.google.com/gmail/api/reference/rest
    """

    def __init__(self, config: GoogleGmailConfig = None):
        logger.debug(f"[GoogleGmailClient] :: init :: >>>>")
        self.config = config or GoogleGmailConfig()
        self.endpoint = self.config.GOOGLE_GMAIL_ENDPOINT

        self.requests = RequestsClient()

    @property
    def _userId(self):
        if not self.config.user_info_email:
            raise Exception(f"[GoogleGmailClient] :: _userId :: ERROR :: {self.config.user_info_email=}")
        return self.config.user_info_email

    def draft_create(self):
        """Creates a new draft with the DRAFT label."""
        api = [
            f'/gmail/v1/users/{self.userId}/drafts',
            f'/upload/gmail/v1/users/{self.userId}/drafts'
        ]
        return self.requests.post(self._base_url(api[0]))

    def draft_delete(self, id: int):
        """Immediately and permanently deletes the specified draft."""
        api = f'/gmail/v1/users/{self.userId}/drafts/{id}'
        return self.requests.delete(self._base_url(api))

    def draft_get(self, id: int):
        """Gets the specified draft."""
        api = f'/gmail/v1/users/{self.userId}/drafts/{id}'
        return self.requests.get(self._base_url(api))

    def draft_list(self):
        """Lists the drafts in the user's mailbox."""
        api = f'/gmail/v1/users/{self.userId}/drafts'
        return self.requests.get(self._base_url(api))

    def draft_send(self):
        """Sends the specified, existing draft to the recipients in the To, Cc, and Bcc headers."""
        api = [
            f'/gmail/v1/users/{self.userId}/drafts/send',
            f'/upload/gmail/v1/users/{self.userId}/drafts/send'
        ]
        return self.requests.post(self._base_url(api[0]))

    def draft_update(self, id: int):
        api = [
            f'/gmail/v1/users/{self.userId}/drafts/{id}'
            f'/upload/gmail/v1/users/{self.userId}/drafts/{id}'
        ]
        return self.requests.put(self._base_url(api[0]))

    def history_list(self):
        """Lists the history of all changes to the given mailbox."""
        api = f'/gmail/v1/users/{self.userId}/history'
        return self.requests.get(self._base_url(api))

    def labels_create(self, label: str):
        """Creates a new label."""
        logger.debug(f"[GoogleGmailClient] :: labels_create :: {label=} :: >>>>")
        api = f'/gmail/v1/users/{self.userId}/labels'
        api = UsersLabels(userId=self.userId)
        return self.requests.post(self._base_url(api))

    def labels_delete(self, id: int):
        """Immediately and permanently deletes the specified label and
        removes it from any messages and threads that it is applied to."""
        api = f'/gmail/v1/users/{self.userId}/labels/{id}'
        return self.requests.delete(self._base_url(api))

    def labels_get(self, id: int):
        """Gets the specified label."""
        api = f'/gmail/v1/users/{self.userId}/labels/{id}'
        return self.requests.get(self._base_url(api))

    def labels_list(self):
        """Lists all labels in the user's mailbox."""
        api = f'/gmail/v1/users/{self.userId}/labels'
        return self.requests.get(self._base_url(api))

    def labels_patch(self, id: int):
        """Patch the specified label."""
        api = f'/gmail/v1/users/{self.userId}/labels/{id}'
        return self.requests.patch(self._base_url(api))

    def labels_update(self, id: int):
        """Updates the specified label."""
        api = f'/gmail/v1/users/{self.userId}/labels/{id}'
        return self.requests.put(self._base_url(api))

    def users_watch(self):
        """Set up or update a push notification watch on the given user mailbox."""
        api = f'/gmail/v1/users/{self.userId}/watch'
        return self.requests.post(self._base_url(api))

    def users_getProfile(self):
        """Gets the current user's Gmail profile."""
        api = f'/gmail/v1/users/{self.userId}/profile'
        return self.requests.get(self._base_url(api))

    def users_stop(self):
        """Stop receiving push notifications for the given user mailbox."""
        api = f'/gmail/v1/users/{self.userId}/stop'
        return self.requests.post(self._base_url(api))
