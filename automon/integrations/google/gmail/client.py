import io
import os
import bs4
import email
import email.mime.text
import email.mime.multipart
import email.mime.image
import email.mime.audio
import email.mime.base
import mimetypes
import googleapiclient.discovery

import automon
import automon.helpers
import automon.helpers.tempfileWrapper

from automon.helpers.loggingWrapper import LoggingClient, DEBUG
from automon.integrations.requestsWrapper import RequestsClient

from .config import GoogleGmailConfig
from .v1 import *
from ..gmail import v1

logger = LoggingClient.logging.getLogger(__name__)
logger.setLevel(DEBUG)


class GoogleGmailClient:
    v1 = v1
    _temp = automon.helpers.tempfileWrapper.Tempfile
    _sleep = automon.helpers.Sleeper
    _bs4 = bs4

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

    def draft_create(self,
                     threadId: str = None,
                     raw: str = None,
                     draft_subject: str = None,
                     draft_from: str = None,
                     draft_to: list = [],
                     draft_cc: list = [],
                     draft_bc: list = [],
                     draft_body: str = None,
                     draft_attachments: [EmailAttachment] = None,
                     **kwargs) -> Draft:
        """Creates a new draft with the DRAFT label."""
        if raw:
            raw = base64.urlsafe_b64encode(raw.encode()).decode()
        else:
            if type(draft_to) is str:
                draft_to = [draft_to]

            if type(draft_cc) is str:
                draft_cc = [draft_cc]

            if type(draft_bc) is str:
                draft_bc = [draft_bc]

            email_build = email.mime.multipart.MIMEMultipart()
            email_build['Subject'] = draft_subject
            email_build['From'] = draft_from
            email_build['To'] = ', '.join(draft_to)
            email_build['Cc'] = ', '.join(draft_cc)
            email_build['Bc'] = ', '.join(draft_bc)

            draft_body = email.mime.text.MIMEText(draft_body)
            email_build.attach(draft_body)

            attachments = []

            for attachment in draft_attachments:

                if not attachment:
                    continue

                filename = attachment.filename
                bytes_ = attachment.bytes_
                mimeType = attachment.mimeType
                content_type = attachment.content_type
                encoding = attachment.encoding

                _temp_file = self._temp.make_temp_file()[1]
                with open(_temp_file, 'wb') as _temp_write:
                    _temp_write.write(bytes_)

                if mimeType is None or not content_type is None and encoding is None:
                    _temp_file = self._temp.make_temp_file()[1]
                    with open(_temp_file, 'wb') as _temp_write:
                        _temp_write.write(bytes_)

                    content_type, encoding = mimetypes.guess_type(_temp_file)
                    os.remove(_temp_file)

                if content_type is None or encoding is None:
                    content_type = 'application'
                    encoding = 'octet-stream'

                if content_type == 'text':
                    msg = email.mime.text.MIMEText(bytes_.decode("utf-8"), _subtype=encoding)

                elif content_type == 'image':
                    msg = email.mime.image.MIMEImage(bytes_, _subtype=encoding)

                elif content_type == 'audio':
                    msg = email.mime.audio.MIMEAudio(bytes_, _subtype=encoding)

                else:

                    content_type = 'application'
                    encoding = 'octet-stream'

                    msg = email.mime.base.MIMEBase(content_type, encoding)
                    msg.set_payload(bytes_)

                msg.add_header('Content-Disposition', 'attachment', filename=filename)
                email_build.attach(msg)
                attachments.append(msg)

                # add previous message
                _previous_message = self.messages_get_automon(id=threadId)
                _wrote = f"{_previous_message.automon_sender.value} wrote:\n"
                _previous_message = _previous_message.automon_attachments.attachments[0].body.automon_data_bs4.html.text
                _previous_message = _previous_message.split('\n')
                _previous_message = [f">{x}" for x in _previous_message]
                _previous_message = '\n'.join(_previous_message)

                _previous_message = (f"\n{_wrote}"
                                     f"\n{_previous_message}")

                msg = email.mime.text.MIMEText(_previous_message)
                email_build.attach(msg)

            raw = base64.urlsafe_b64encode(email_build.as_string().encode()).decode()

        api = UsersDrafts(self._userId).create
        message = Message(raw=raw, threadId=threadId, **kwargs)
        data = Draft(message=message).to_dict()
        self.requests.post(api, headers=self.config.headers, json=data)
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
        api = UsersDrafts(self._userId).get(id)
        params = dict(
            format=format,
        )
        self.requests.get(api, headers=self.config.headers, params=params)
        return Draft().update_dict(self.requests.to_dict())

    def draft_list(self,
                   maxResults: int = 100,
                   pageToken: str = '',
                   q: bool = '',
                   includeSpamTrash: bool = None) -> DraftList:
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
        return DraftList().update_dict(self.requests.to_dict())

    def draft_list_automon(self, *args, **kwargs):
        """Enhanced `message_get`"""
        drafts = self.draft_list(*args, **kwargs)
        drafts = self._improved_draft_list(drafts=drafts)
        return drafts

    def draft_send(self):
        """Sends the specified, existing draft to the recipients in the To, Cc, and Bcc headers."""
        api = UsersDrafts(self._userId).send
        data = Draft().to_dict()
        self.requests.post(api, headers=self.config.headers, json=data)
        return self.requests.to_dict()

    def draft_update(self, id: int):
        api = UsersDrafts(self._userId).update(id)
        data = Draft().to_dict()
        self.requests.put(api, headers=self.config.headers, json=data)
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
                    self.config.credentials_pickle_save()
                    if self.config.userinfo():
                        return True
        return False

    def labels_create(self,
                      name: str,
                      color: Color = None,
                      backgroundColor: str = None,
                      textColor: str = None):
        """Creates a new label.

        Max labels 10,000
        """
        logger.debug(f"[GoogleGmailClient] :: labels_create :: {name=} :: >>>>")
        if color:
            color = color
        else:
            color = Color(backgroundColor=backgroundColor, textColor=textColor)
        api = UsersLabels(userId=self._userId).create
        data = Label(name=name, color=color).to_dict()
        self.requests.post(api, headers=self.config.headers, json=data)
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
        return Label().update_dict(self.requests.to_dict())

    def labels_get_by_name(self, name: str) -> Label:
        """Gets label by name"""
        self.labels_list()
        labels = self.requests.to_dict()['labels']
        for label in labels:
            if label['name'] == name:
                return Label().update_dict(label)

    def labels_list(self):
        """Lists all labels in the user's mailbox."""
        api = UsersLabels(self._userId).list
        self.requests.get(api, headers=self.config.headers)
        return self.requests.to_dict()

    def labels_patch(self, id: str):
        """Patch the specified label."""
        api = UsersLabels(self._userId).patch(id)
        data = Label().to_dict()
        self.requests.patch(api, headers=self.config.headers, json=data)
        return self.requests.to_dict()

    def labels_update(self,
                      id: str,
                      color: Color = None,
                      backgroundColor: str = None,
                      textColor: str = None):
        """Updates the specified label."""
        if color:
            color = color
        else:
            color = Color(backgroundColor=backgroundColor, textColor=textColor)

        api = UsersLabels(self._userId).update(id)
        data = Label(id=id, color=color).to_dict()
        self.requests.put(api, headers=self.config.headers, json=data)
        return self.requests.to_dict()

    def _improved_draft_list(self, drafts: DraftList) -> DraftList:
        """Better drafts."""

        if hasattr(drafts, 'drafts'):

            _automon_drafts = []

            _drafts = drafts.drafts
            for _draft in _drafts:
                _draft = Draft().update_dict(_draft)
                _draft.message = Message().update_dict(_draft.message)
                _draft.message = self.messages_get_automon(_draft.message.id)

                _automon_drafts.append(_draft)

            setattr(drafts, 'drafts', _automon_drafts)

        return drafts

    def _improved_messages_get(self, message: Message):
        """Better labels."""

        if hasattr(message, 'labelIds'):
            setattr(message, 'automon_labels', [self.labels_get(x) for x in message.labelIds])

        return message

    def _improved_messages_list(self, messages: MessageList) -> MessageList:
        """Better messages."""

        for _message in messages.messages:

            # update messages
            _message.update_dict(
                self.messages_get_automon(id=_message.id)
            )

            # update attachments
            if hasattr(_message, 'payload'):

                if hasattr(_message.payload, 'parts'):

                    for _payload_part in _message.payload.parts:
                        if hasattr(_payload_part.body, 'attachmentId'):
                            _attachmentId = _payload_part.body.attachmentId
                            _payload_part.body.update_dict(
                                self.messages_attachments_get(messageId=_message.id,
                                                              attachmentId=_attachmentId))

                            if hasattr(_payload_part.body, 'automon_attachment'):
                                setattr(_payload_part, 'automon_attachment', _payload_part.body.automon_attachment)

        return messages

    def messages_attachments_get(self,
                                 messageId: str,
                                 attachmentId: str) -> MessagePartBody:
        """
        Gets the specified message attachment.

        The URL uses gRPC Transcoding syntax.

        Path parameters
        Parameters
        userId
        string

        The user's email address. The special value me can be used to indicate the authenticated user.

        messageId
        string

        The ID of the message containing the attachment.

        id
        string

        The ID of the attachment.
        """
        if attachmentId is None:
            return

        api = UsersMessagesAttachments(self._userId).get(messageId=messageId, id=attachmentId)
        self.requests.get(api, headers=self.config.headers)
        return MessagePartBody().update_dict(self.requests.to_dict())

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

    def messages_get_automon(self, *args, **kwargs, ):
        """Enhanced `message_get`"""
        message = self.messages_get(*args, **kwargs)
        return self._improved_messages_get(message=message)

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
                        addLabelIds: list = [],
                        removeLabelIds: list = []):
        """Modifies the labels on the specified message."""
        if len(addLabelIds) > 100 or len(removeLabelIds) > 100:
            raise Exception(
                f"[GoogleGmailClient] :: messages_modify :: ERROR :: {len(addLabelIds)=} {len(addLabelIds)=} > 100")

        api = UsersMessages(self._userId).modify(id)
        data = {
            "addLabelIds": addLabelIds,
            "removeLabelIds": removeLabelIds
        }
        self.requests.post(api, headers=self.config.headers, json=data)
        return Message().update_dict(self.requests.to_dict())

    def messages_send(self):
        """Sends the specified message to the recipients in the To, Cc, and Bcc headers. For example usage, see Sending email."""
        api = UsersMessages(self._userId).send
        data = Message().to_dict()
        self.requests.post(api, headers=self.config.headers, json=data)
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
