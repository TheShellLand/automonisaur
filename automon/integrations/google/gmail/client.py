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

    def draft_create(self, raw: str, threadId: str = None, **kwargs) -> Draft:
        """Creates a new draft with the DRAFT label."""
        api = UsersDrafts(self._userId).create
        message = Message(raw=raw, threadId=threadId, **kwargs).to_dict()
        data = Draft(message=message)
        self.requests.post(api, headers=self.config.headers, json=data.__dict__)
        return Draft().update_dict(self.requests.to_dict())

    def draft_delete(self, id: int):
        """Immediately and permanently deletes the specified draft."""
        api = UsersDrafts(self._userId).delete(id)
        self.requests.delete(api, headers=self.config.headers)
        return self.requests.to_dict()

    def draft_get(self,
                  id: int,
                  format: Format = Format.full) -> Draft:
        """Gets the specified draft."""
        api = f'/gmail/v1/users/{self._userId}/drafts/{id}'
        params = dict(
            format=format,
        )
        self.requests.get(api, headers=self.config.headers, params=params)
        return Draft().update_dict(self.requests.to_dict())

    def draft_list(self,
                   maxResults: int = 100,
                   pageToken: str = '',
                   q: bool = '',
                   includeSpamTrash: bool = None):
        """Lists the drafts in the user's mailbox.

        Parameters
        maxResults
        integer (uint32 format)

        Maximum number of drafts to return. This field defaults to 100. The maximum allowed value for this field is 500.

        pageToken
        string

        Page token to retrieve a specific page of results in the list.

        q
        string

        Only return draft messages matching the specified query. Supports the same query format as the Gmail search box. For example, "from:someuser@example.com rfc822msgid:<somemsgid@example.com> is:unread".

        includeSpamTrash
        boolean

        Include drafts from SPAM and TRASH in the results.
        """
        if maxResults > 500:
            raise Exception(f"[GoogleGmailClient] :: draft_list :: ERROR :: {maxResults=} > 500")

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
        self.requests.post(api, headers=self.config.headers, json=data.__dict__)
        return self.requests.to_dict()

    def draft_update(self, id: int):
        api = UsersDrafts(self._userId).update(id)
        data = Draft()
        self.requests.put(api, headers=self.config.headers, json=data.__dict__)
        return self.requests.to_dict()

    def history_list(self,
                     startHistoryId: str,
                     maxResults: int = 100,
                     pageToken: str = None,
                     labelId: str = None,
                     historyTypes: HistoryType = None):
        """Lists the history of all changes to the given mailbox."""
        if maxResults > 500:
            raise Exception(f"[GoogleGmailClient] :: history_list :: ERROR :: {maxResults=} > 500")

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
            if self.config.Credentials():
                if self.config.refresh_token():
                    return True
        return False

    def labels_create(self, name: str):
        """Creates a new label.

        Max labels 10,000
        """
        logger.debug(f"[GoogleGmailClient] :: labels_create :: {name=} :: >>>>")
        api = UsersLabels(userId=self._userId).create
        data = Label(name=name)
        self.requests.post(api, headers=self.config.headers, json=data.__dict__)
        return Label().update_dict(self.requests.to_dict())

    def labels_delete(self, id: str):
        """Immediately and permanently deletes the specified label and removes it from any messages and threads that it is applied to."""
        api = UsersLabels(self._userId).delete(id)
        self.requests.delete(api, headers=self.config.headers)
        if self.requests.status_code == 204:
            return True
        return False

    def labels_get(self, id: str):
        """Gets the specified label."""
        api = UsersLabels(self._userId).get(id)
        self.requests.get(api, headers=self.config.headers)
        return self.requests.to_dict()

    def labels_get_by_name(self, name: str):
        """Gets label by name"""
        self.labels_list()
        labels = self.requests.to_dict()['labels']
        for label in labels:
            if label['name'] == name:
                return label

    def labels_list(self):
        """Lists all labels in the user's mailbox."""
        api = UsersLabels(self._userId).list
        self.requests.get(api, headers=self.config.headers)
        return self.requests.to_dict()

    def labels_patch(self, id: str):
        """Patch the specified label."""
        api = UsersLabels(self._userId).patch(id)
        data = Label()
        self.requests.patch(api, headers=self.config.headers, json=data.__dict__)
        return self.requests.to_dict()

    def labels_update(self, id: str):
        """Updates the specified label."""
        api = UsersLabels(self._userId).update(id)
        data = Label()
        self.requests.put(api, headers=self.config.headers, json=data.__dict__)
        return self.requests.to_dict()

    def _improved_messages_get(self, message: Message):
        """Better labels."""

        if hasattr(message, 'labelIds'):
            message.__dict__['automon_labelIds'] = [self.labels_get(x) for x in message.labelIds]

        return message

    def _improved_messages_list(self, messages: MessageList) -> MessageList:
        """Better messages."""

        messages_automon = []
        messages_ = messages.messages
        for msg in messages_:
            id = msg['id']
            threadId = msg['threadId']
            messages_automon.append(
                self.messages_get_automon(id=id)
            )
        messages.automon_messages = messages_automon

        return messages

    def messages_batchDelete(self, ids: list):
        """Deletes many messages by message ID. Provides no guarantees that messages were not already deleted or even existed at all."""
        if type(ids) is not list:
            raise Exception(f"[GoogleGmailClient] :: messages_batchDelete :: ERROR :: {type(ids)=} is not list")

        api = UsersMessages(self._userId).batchDelete
        data = {
            "ids": ids
        }
        self.requests.post(api, headers=self.config.headers, json=data)
        return self.requests.to_dict()

    def messages_batchModify(self,
                             ids: list = None,
                             addLabelIds: list = None,
                             removeLabelIds: list = None):
        """Modifies the labels on the specified messages."""
        if type(ids) is not list:
            raise Exception(f"[GoogleGmailClient] :: messages_batchModify :: ERROR :: {type(ids)=} is not list")

        api = UsersMessages(self._userId).batchModify
        data = {
            "ids": ids,
            "addLabelIds": addLabelIds,
            "removeLabelIds": removeLabelIds
        }
        self.requests.post(api, headers=self.config.headers, json=data)
        return self.requests.to_dict()

    def messages_delete(self, id: int):
        """Immediately and permanently deletes the specified message. This operation cannot be undone. Prefer messages.trash instead."""
        api = UsersMessages(self._userId).delete(id)
        self.requests.delete(api, headers=self.config.headers)
        return self.requests.to_dict()

    def messages_get(self,
                     id: str,
                     format: Format = Format.full,
                     metadataHeaders: list = None) -> Message:
        """Gets the specified message."""
        api = UsersMessages(self._userId).get(id)
        params = dict(
            format=format,
            metadataHeaders=metadataHeaders
        )
        self.requests.get(api, headers=self.config.headers, params=params)
        return Message().update_dict(self.requests.to_dict())

    def messages_get_automon(self, *args, **kwargs):
        """Enhanced `message_get`"""
        message = self.messages_get(*args, **kwargs)
        message = self._improved_messages_get(message=message)
        return message

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
                      includeSpamTrash: bool = False) -> MessageList:
        """Lists the messages in the user's mailbox."""
        logger.debug(
            f"[GoogleGmailClient] :: message_list :: {maxResults=} :: {pageToken=} :: {q=} :: {labelIds=} :: {includeSpamTrash=}")

        if maxResults > 500:
            raise Exception(f"[GoogleGmailClient] :: message_list :: ERROR :: {maxResults=} > 500")

        api = UsersMessages(self._userId).list
        params = dict(
            maxResults=maxResults,
            pageToken=pageToken,
            q=q,
            labelIds=labelIds,
            includeSpamTrash=includeSpamTrash
        )
        self.requests.get(api, headers=self.config.headers, params=params)

        logger.info(f"[GoogleGmailClient] :: message_list :: done")
        return MessageList().update_dict(self.requests.to_dict())

    def messages_list_automon(self, *args, **kwargs):
        """Enhanced `message_list`"""
        messages = self.messages_list(*args, **kwargs)
        if messages:
            messages = self._improved_messages_list(messages=messages)
        return messages

    def messages_modify(self,
                        id: int,
                        addLabelIds: list = None,
                        removeLabelIds: list = None):
        """Modifies the labels on the specified message."""
        if len(addLabelIds) or len(removeLabelIds) > 100:
            raise Exception(
                f"[GoogleGmailClient] :: messages_modify :: ERROR :: {len(addLabelIds)=} {len(addLabelIds)=} > 100")

        api = UsersMessages(self._userId).modify(id)
        data = {
            "addLabelIds": addLabelIds,
            "removeLabelIds": removeLabelIds
        }
        self.requests.post(api, headers=self.config.headers, json=data)
        return self.requests.to_dict()

    def messages_send(self):
        """Sends the specified message to the recipients in the To, Cc, and Bcc headers. For example usage, see Sending email."""
        api = UsersMessages(self._userId).send
        data = Message()
        self.requests.post(api, headers=self.config.headers, json=data.__dict__)
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
