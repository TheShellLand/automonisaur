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
        api = UsersDrafts(self._userId)
        return self.requests.post(api, headers=self.config.headers)

    def draft_delete(self, id: int):
        """Immediately and permanently deletes the specified draft."""
        api = UsersDrafts(self._userId).delete(id)
        return self.requests.delete(api, headers=self.config.headers)

    def draft_get(self, id: int):
        """Gets the specified draft."""
        api = f'/gmail/v1/users/{self._userId}/drafts/{id}'
        return self.requests.get(api, headers=self.config.headers)

    def draft_list(self,
                   maxResults: int = 100,
                   pageToken: str = '',
                   q: bool = '',
                   includeSpamTrash: bool = None):
        """Lists the drafts in the user's mailbox."""
        if maxResults > 500:
            raise

        api = UsersDrafts(self._userId).list
        params = dict(
            maxResults=maxResults,
            pageToken=pageToken,
            q=q,
            includeSpamTrash=includeSpamTrash,
        )
        return self.requests.get(api, headers=self.config.headers, params=params)

    def draft_send(self):
        """Sends the specified, existing draft to the recipients in the To, Cc, and Bcc headers."""
        api = UsersDrafts(self._userId).send
        data = Draft()
        return self.requests.post(api, headers=self.config.headers, data=data.__dict__)

    def draft_update(self, id: int):
        api = UsersDrafts(self._userId).update(id)
        data = Draft()
        return self.requests.put(api, headers=self.config.headers, data=data.__dict__)

    def history_list(self,
                     startHistoryId: str,
                     maxResults: int = 100,
                     pageToken: str = None,
                     labelId: str = None,
                     historyTypes: HistoryType = None):
        """Lists the history of all changes to the given mailbox."""
        if maxResults > 500:
            raise

        api = UsersHistory(self._userId).list
        params = dict(
            maxResults=maxResults,
            pageToken=pageToken,
            startHistoryId=startHistoryId,
            labelId=labelId,
            historyTypes=historyTypes
        )
        return self.requests.get(api, headers=self.config.headers, params=params)

    def is_ready(self):
        return True

    def labels_create(self, label: str):
        """Creates a new label."""
        logger.debug(f"[GoogleGmailClient] :: labels_create :: {label=} :: >>>>")
        api = UsersLabels(userId=self._userId)
        data = Label()
        return self.requests.post(api, headers=self.config.headers, data=data.__dict__)

    def labels_delete(self, id: int):
        """Immediately and permanently deletes the specified label and
        removes it from any messages and threads that it is applied to."""
        api = UsersLabels(self._userId).delete(id)
        return self.requests.delete(api, headers=self.config.headers)

    def labels_get(self, id: int):
        """Gets the specified label."""
        api = UsersLabels(self._userId).get(id)
        return self.requests.get(api, headers=self.config.headers)

    def labels_list(self):
        """Lists all labels in the user's mailbox."""
        api = UsersLabels(self._userId).list
        return self.requests.get(api, headers=self.config.headers)

    def labels_patch(self, id: int):
        """Patch the specified label."""
        api = UsersLabels(self._userId).patch(id)
        data = Label()
        return self.requests.patch(api, headers=self.config.headers, data=data.__dict__)

    def labels_update(self, id: int):
        """Updates the specified label."""
        api = UsersLabels(self._userId).update(id)
        data = Label()
        return self.requests.put(api, headers=self.config.headers, data=data.__dict__)

    def users_watch(self):
        """Set up or update a push notification watch on the given user mailbox."""
        api = f'/gmail/v1/users/{self._userId}/watch'
        return self.requests.post(api, headers=self.config.headers)

    def users_getProfile(self):
        """Gets the current user's Gmail profile."""
        api = Users(self._userId).getProfile
        return self.requests.get(api, headers=self.config.headers)

    def users_stop(self):
        """Stop receiving push notifications for the given user mailbox."""
        api = f'/gmail/v1/users/{self._userId}/stop'
        return self.requests.post(api, headers=self.config.headers)
