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
        data = Draft()
        self.requests.post(api, headers=self.config.headers, data=data.__dict__)
        return self.requests.to_dict()

    def draft_delete(self, id: int):
        """Immediately and permanently deletes the specified draft."""
        api = UsersDrafts(self._userId).delete(id)
        self.requests.delete(api, headers=self.config.headers)
        return self.requests.to_dict()

    def draft_get(self,
                  id: int,
                  format: Format = None):
        """Gets the specified draft."""
        api = f'/gmail/v1/users/{self._userId}/drafts/{id}'
        params = dict(
            format=format,
        )
        self.requests.get(api, headers=self.config.headers, params=params)
        return self.requests.to_dict()

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
        self.requests.get(api, headers=self.config.headers, params=params)
        return self.requests.to_dict()

    def draft_send(self):
        """Sends the specified, existing draft to the recipients in the To, Cc, and Bcc headers."""
        api = UsersDrafts(self._userId).send
        data = Draft()
        self.requests.post(api, headers=self.config.headers, data=data.__dict__)
        return self.requests.to_dict()

    def draft_update(self, id: int):
        api = UsersDrafts(self._userId).update(id)
        data = Draft()
        self.requests.put(api, headers=self.config.headers, data=data.__dict__)
        return self.requests.to_dict()

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
        self.requests.get(api, headers=self.config.headers, params=params)

    def is_ready(self):
        if self.config.is_ready():
            return True

    def labels_create(self, label: str):
        """Creates a new label."""
        logger.debug(f"[GoogleGmailClient] :: labels_create :: {label=} :: >>>>")
        api = UsersLabels(userId=self._userId)
        data = Label()
        self.requests.post(api, headers=self.config.headers, data=data.__dict__)
        return self.requests.to_dict()

    def labels_delete(self, id: int):
        """Immediately and permanently deletes the specified label and
        removes it from any messages and threads that it is applied to."""
        api = UsersLabels(self._userId).delete(id)
        self.requests.delete(api, headers=self.config.headers)
        return self.requests.to_dict()

    def labels_get(self, id: int):
        """Gets the specified label."""
        api = UsersLabels(self._userId).get(id)
        self.requests.get(api, headers=self.config.headers)
        return self.requests.to_dict()

    def labels_list(self):
        """Lists all labels in the user's mailbox."""
        api = UsersLabels(self._userId).list
        self.requests.get(api, headers=self.config.headers)
        return self.requests.to_dict()

    def labels_patch(self, id: int):
        """Patch the specified label."""
        api = UsersLabels(self._userId).patch(id)
        data = Label()
        self.requests.patch(api, headers=self.config.headers, data=data.__dict__)
        return self.requests.to_dict()

    def labels_update(self, id: int):
        """Updates the specified label."""
        api = UsersLabels(self._userId).update(id)
        data = Label()
        self.requests.put(api, headers=self.config.headers, data=data.__dict__)
        return self.requests.to_dict()

    def messages_batchDelete(self, ids: list):
        """Deletes many messages by message ID. Provides no guarantees that messages were not already deleted or even existed at all."""
        if type(ids) is not list:
            raise

        api = UsersMessages(self._userId).batchDelete
        data = {
            "ids": ids
        }
        self.requests.post(api, headers=self.config.headers, data=data)
        return self.requests.to_dict()

    def messages_batchModify(self,
                             ids: list = None,
                             addLabelIds: list = None,
                             removeLabelIds: list = None):
        """Modifies the labels on the specified messages."""
        if type(ids) is not list:
            raise

        api = UsersMessages(self._userId).batchModify
        data = {
            "ids": ids,
            "addLabelIds": addLabelIds,
            "removeLabelIds": removeLabelIds
        }
        self.requests.post(api, headers=self.config.headers, data=data)
        return self.requests.to_dict()

    def messages_delete(self, id: int):
        """Immediately and permanently deletes the specified message. This operation cannot be undone. Prefer messages.trash instead."""
        api = UsersMessages(self._userId).delete(id)
        self.requests.delete(api, headers=self.config.headers)
        return self.requests.to_dict()

    def messages_get(self,
                     id: str,
                     format: Format = None,
                     metadataHeaders: list = None) -> Message:
        """Gets the specified message."""
        api = UsersMessages(self._userId).get(id)
        params = dict(
            format=format,
            metadataHeaders=metadataHeaders
        )
        self.requests.get(api, headers=self.config.headers, params=params)
        return Message().update_(self.requests.to_dict())

    def messages_import(self,
                        internalDateSource: InternalDateSource = None,
                        neverMarkSpam: bool = None,
                        processForCalendar: bool = None,
                        deleted: bool = None):
        """Imports a message into only this user's mailbox, with standard email delivery scanning and classification similar to receiving via SMTP. This method doesn't perform SPF checks, so it might not work for some spam messages, such as those attempting to perform domain spoofing. This method does not send a message."""
        api = UsersMessages(self._userId).import_
        params = dict(
            internalDateSource=internalDateSource,
            neverMarkSpam=neverMarkSpam,
            processForCalendar=processForCalendar,
            deleted=deleted
        )
        self.requests.post(api, headers=self.config.headers, params=params)
        return self.requests.to_dict()

    def messages_insert(self,
                        internalDateSource: InternalDateSource = None,
                        deleted: bool = None):
        """Directly inserts a message into only this user's mailbox similar to IMAP APPEND, bypassing most scanning and classification. Does not send a message."""
        api = UsersMessages(self._userId).insert
        params = dict(
            internalDateSource=internalDateSource,
            deleted=deleted
        )
        self.requests.post(api, headers=self.config.headers, params=params)
        return self.requests.to_dict()

    def messages_list(self,
                      maxResults: int = 100,
                      pageToken: str = None,
                      q: str = None,
                      labelIds: str = None,
                      includeSpamTrash: bool = False
                      ):
        """Lists the messages in the user's mailbox."""
        if maxResults > 500:
            raise

        api = UsersMessages(self._userId).list
        params = dict(
            maxResults=maxResults,
            pageToken=pageToken,
            q=q,
            labelIds=labelIds,
            includeSpamTrash=includeSpamTrash
        )
        self.requests.get(api, headers=self.config.headers, params=params)
        return self.requests.to_dict()

    def messages_modify(self,
                        id: int,
                        addLabelIds: list = None,
                        removeLabelIds: list = None):
        """Modifies the labels on the specified message."""
        if len(addLabelIds) or len(removeLabelIds) > 100:
            raise

        api = UsersMessages(self._userId).modify(id)
        data = {
            "addLabelIds": addLabelIds,
            "removeLabelIds": removeLabelIds
        }
        self.requests.post(api, headers=self.config.headers, data=data)
        return self.requests.to_dict()

    def messages_send(self):
        """Sends the specified message to the recipients in the To, Cc, and Bcc headers. For example usage, see Sending email."""
        api = UsersMessages(self._userId).send
        data = Message()
        self.requests.post(api, headers=self.config.headers, data=data.__dict__)
        return self.requests.to_dict()

    def messages_trash(self, id: int):
        """Moves the specified message to the trash."""
        api = UsersMessages(self._userId).trash(id)
        self.requests.post(api, headers=self.config.headers)
        return self.requests.to_dict()

    def messages_untrash(self, id: int):
        """Removes the specified message from the trash."""
        api = UsersMessages(self._userId).untrash(id)
        self.requests.post(api, headers=self.config.headers)
        return self.requests.to_dict()

    def users_watch(self):
        """Set up or update a push notification watch on the given user mailbox."""
        api = f'/gmail/v1/users/{self._userId}/watch'
        self.requests.post(api, headers=self.config.headers)
        return self.requests.to_dict()

    def users_getProfile(self):
        """Gets the current user's Gmail profile."""
        api = Users(self._userId).getProfile
        self.requests.get(api, headers=self.config.headers)
        return self.requests.to_dict()

    def users_stop(self):
        """Stop receiving push notifications for the given user mailbox."""
        api = f'/gmail/v1/users/{self._userId}/stop'
        self.requests.post(api, headers=self.config.headers)
        return self.requests.to_dict()
