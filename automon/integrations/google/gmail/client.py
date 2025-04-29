import io
import os
import bs4
import email
import email.encoders
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


class AutomonLabels:
    labels = {
        'automon': 'automon',
        'resume': 'automon/resume',
        'analyze': 'automon/analyze',
        "retry": 'automon/retry',
        'relevant': 'automon/relevant',
        "remote": 'automon/remote',
        "welcome": 'automon/welcome',
        "help": 'automon/help',
        "auto_reply_enabled": 'automon/auto reply enabled',
        "user_action_required": 'automon/user action required',
    }

    def __init__(self):
        self._reset_labels = False

        self._color_default = Color(backgroundColor='#653e9b', textColor='#e4d7f5')
        self._color_resume = Color(backgroundColor='#b65775', textColor='#ffffff')
        self._color_error = Color(backgroundColor='#cc3a21', textColor='#ffd6a2')
        self._color_enabled = Color(backgroundColor='#076239', textColor='#b9e4d0')
        self._color_welcome = Color(backgroundColor='#8e63ce', textColor='#ffffff')

        # required
        self.automon = Label(name=self.labels.get('automon'), color=self._color_default)

        # welcome
        self.welcome = Label(name=self.labels.get('welcome'), color=self._color_welcome)
        self.help = Label(name=self.labels.get('help'), color=self._color_welcome)

        # resume
        self.resume = Label(name=self.labels.get('resume'), color=self._color_resume)

        # analyze
        self.analyze = Label(name=self.labels.get('analyze'), color=self._color_default)

        # general
        self.draft = Label(name='DRAFT', id='DRAFT')
        self.sent = Label(name='SENT', id='SENT')
        self.unread = Label(name='UNREAD', id='UNREAD')
        self.trash = Label(name='TRASH', id='TRASH')

        # allow auto reply
        self.auto_reply_enabled = Label(name=self.labels.get('auto_reply_enabled'), color=self._color_enabled)

        # retry draft
        self.retry = Label(name=self.labels.get('retry'), color=self._color_error)

        # relevance
        self.relevant = Label(name=self.labels.get('relevant'), color=self._color_default)

        # remote
        self.remote = Label(name=self.labels.get('remote'), color=self._color_default)

        # need user input
        self.user_action_required = Label(name=self.labels.get('user_action_required'), color=self._color_error)

    @property
    def all_labels(self):
        return [
            getattr(self, x) for x in self.labels.keys()
            if not x.startswith("_")
            if not x == 'automon'
        ]


class GoogleGmailClient:
    v1 = v1
    _temp = automon.helpers.tempfileWrapper.Tempfile
    _sleep = automon.helpers.Sleeper
    _bs4 = bs4
    _automon_labels = AutomonLabels()

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
        if self.config.user_info_email:
            return self.config.user_info_email

    def draft_create(self,
                     threadId: str = None,
                     raw: str = None,
                     draft_subject: str = None,
                     draft_from: str = None,
                     draft_to: list = [],
                     draft_cc: list = [],
                     draft_bc: list = [],
                     draft_body: str = '',
                     draft_attachments: [EmailAttachment] = [],
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
                    email.encoders.encode_base64(msg)

                msg.add_header('Content-Disposition', 'attachment', filename=filename)
                email_build.attach(msg)
                attachments.append(msg)

            raw = base64.urlsafe_b64encode(email_build.as_string().encode()).decode()

        api = UsersDrafts(self._userId).create
        message = Message(raw=raw, threadId=threadId, **kwargs)
        data = Draft(message=message).to_dict()
        self.requests.post(api, headers=self.config.headers, json=data)
        return Draft().update_dict(self.requests.to_dict())

    def draft_delete(self, id: str):
        """Immediately and permanently deletes the specified draft."""
        api = UsersDrafts(self._userId).delete(id)
        self.requests.delete(api, headers=self.config.headers)
        return self.requests.to_dict()

    def draft_get(self,
                  id: str or Draft,
                  format: Format = Format.full) -> Draft:
        """Gets the specified draft."""
        if type(id) is Draft:
            id = id.id

        api = UsersDrafts(self._userId).get(id)
        params = dict(
            format=format,
        )
        self.requests.get(api, headers=self.config.headers, params=params)
        return Draft().update_dict(self.requests.to_dict())

    def draft_get_automon(self, *args, **kwargs):
        draft = self.draft_get(*args, **kwargs)
        return self._improved_draft_get(draft=draft)

    def draft_list(self,
                   q: bool = '',
                   maxResults: int = 100,
                   pageToken: str = '',
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
        logger.info(f"[GoogleGmailClient] :: draft_list :: done")
        return DraftList().update_dict(self.requests.to_dict())

    def draft_list_automon(self, *args, **kwargs):
        """Enhanced `message_get`"""
        drafts = self.draft_list(*args, **kwargs)
        drafts = self._improved_draft_list(drafts=drafts)
        return drafts

    def draft_send(self, draft: Draft) -> Message:
        """Sends the specified, existing draft to the recipients in the To, Cc, and Bcc headers."""
        logger.debug(f"[GoogleGmailClient] :: draft_send :: {draft=}")
        api = UsersDrafts(self._userId).send
        data = draft.to_dict()
        self.requests.post(api, headers=self.config.headers, json=data)
        logger.info(f"[GoogleGmailClient] :: draft_send :: done")
        return Message().update_dict(self.requests.to_dict())

    def draft_update(self, id: str) -> Draft:
        api = UsersDrafts(self._userId).update(id)
        data = Draft().to_dict()
        self.requests.put(api, headers=self.config.headers, json=data)
        return Draft().update_dict(self.requests.to_dict())

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

        return self.requests.to_dict()

    def is_ready(self):
        if self.config.is_ready():
            if self.config.Credentials():
                if self.config.refresh_token():
                    self.config.credentials_pickle_save()
                    if self.config.userinfo():
                        return True
        logger.error(f"[GoogleGmailClient] :: is_ready :: ERROR :: not ready")
        return False

    def labels_create(self,
                      name: str,
                      color: Color = None) -> Label:
        """Creates a new label.

        Max labels 10,000
        """
        logger.debug(f"[GoogleGmailClient] :: labels_create :: {name=} :: >>>>")
        api = UsersLabels(userId=self._userId).create
        json = Label(name=name, color=color).to_dict()
        self.requests.post(api, headers=self.config.headers, json=json)
        logger.info(f"[GoogleGmailClient] :: labels_create :: done")
        return Label().update_dict(self.requests.to_dict())

    def labels_delete(self, id: str) -> bool:
        """Immediately and permanently deletes the specified label and removes it from any messages and threads that it is applied to."""
        if type(id) is Label:
            id = id.id

        api = UsersLabels(self._userId).delete(id)
        self.requests.delete(api, headers=self.config.headers)
        if self.requests.status_code == 204:
            return True
        return False

    def labels_get(self, id: str) -> Label:
        """Gets the specified label."""
        if type(id) is Label:
            id = id.id

        logger.debug(f"[GoogleGmailClient] :: labels_get :: {id=}")
        api = UsersLabels(self._userId).get(id)
        self.requests.get(api, headers=self.config.headers)
        label = Label().update_dict(self.requests.to_dict())
        logger.debug(f"[GoogleGmailClient] :: labels_get :: {label.name}")
        logger.info(f"[GoogleGmailClient] :: labels_get :: done")
        return label

    def labels_get_by_name(self, name: str) -> Label:
        """Gets label by name"""
        labels = self.labels_list()
        for label in labels.labels:
            if label.name == name:
                logger.info(f"[GoogleGmailClient] :: labels_get_by_name :: done")
                return Label().update_dict(label)

    def labels_list(self):
        """Lists all labels in the user's mailbox."""
        api = UsersLabels(self._userId).list
        self.requests.get(api, headers=self.config.headers)
        logger.info(f"[GoogleGmailClient] :: labels_list :: done")
        return LabelList().update_dict(self.requests.to_dict())

    def labels_patch(self, id: str):
        """Patch the specified label."""
        if type(id) is Label:
            id = id.id

        api = UsersLabels(self._userId).patch(id)
        data = Label().to_dict()
        self.requests.patch(api, headers=self.config.headers, json=data)
        logger.info(f"[GoogleGmailClient] :: labels_patch :: done")
        return self.requests.to_dict()

    def labels_update(self,
                      id: str or Label,
                      color: Color = None) -> Label:
        """Updates the specified label."""
        if type(id) is Label:
            id = id.id

        api = UsersLabels(self._userId).update(id)
        data = Label(id=id, color=color).to_dict()
        self.requests.put(api, headers=self.config.headers, json=data)
        logger.info(f"[GoogleGmailClient] :: labels_update :: done")
        return Label().update_dict(self.requests.to_dict())

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

    def _improved_draft_get(self, draft: Draft) -> Draft:
        """Better draft."""

        if hasattr(draft, 'message'):
            draft.message = self.messages_get_automon(draft.message.id)

        return draft

    def _improved_messages_get(self, message: Message) -> Message:
        """Better messages."""

        if hasattr(message, 'labelIds'):
            setattr(message, 'automon_labels', [self.labels_get(x) for x in message.labelIds])

        # update attachments
        if hasattr(message, 'payload'):

            if hasattr(message.payload, 'parts'):

                for _payload_part in message.payload.parts:
                    if hasattr(_payload_part.body, 'attachmentId'):
                        _attachmentId = _payload_part.body.attachmentId

                        if _attachmentId:
                            _messages_attachments_get = self.messages_attachments_get(messageId=message.id,
                                                                                      attachmentId=_attachmentId)
                            _payload_part.body.update_dict(_messages_attachments_get)

                        if hasattr(_payload_part.body, 'automon_attachment'):
                            setattr(_payload_part, 'automon_attachment', _payload_part.body.automon_attachment)

        return message

    def _improved_messages_list(self, messages: MessageList) -> MessageList:
        """Better messages."""

        for _message in messages.messages:
            # update messages
            _get = self.messages_get_automon(id=_message.id)
            _message.update_dict(_get)

        return messages

    def _improved_thread_get(self, thread: Thread) -> Thread:
        """Better thread."""

        _get = self.thread_get(id=thread.id)
        thread.update_dict(_get)

        for _message in thread.messages:
            _get_message = self._improved_messages_get(_message)
            _message.update_dict(_get_message)

        return thread

    def _improved_thread_list(self, threads: ThreadList) -> ThreadList:
        """Better thread list."""

        for _thread in threads.threads:
            _get = self.thread_get_automon(id=_thread.id)
            _thread.update_dict(_get)

            for _message in _thread.messages:
                _get_message = self._improved_messages_get(_message)
                _message.update_dict(_get_message)

        return threads

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
        if self.requests.get(api, headers=self.config.headers):
            attachments = MessagePartBody().update_dict(self.requests.to_dict())
            logger.debug(f"[GoogleGmailClient] :: messages_attachments_get :: {attachments=}")
        else:
            raise Exception(f"[GoogleGmailClient] :: messages_attachments_get :: error :: {self.requests}")

        logger.info(f"[GoogleGmailClient] :: messages_attachments_get :: done")
        return attachments

    def messages_batchDelete(self, ids: list):
        """Deletes many messages by message ID. Provides no guarantees that messages were not already deleted or even existed at all."""
        if type(ids) is not list:
            raise Exception(f"[GoogleGmailClient] :: messages_batchDelete :: ERROR :: {type(ids)=} is not list")

        api = UsersMessages(self._userId).batchDelete
        data = {
            "ids": ids
        }
        self.requests.post(api, headers=self.config.headers, json=data)
        logger.info(f"[GoogleGmailClient] :: messages_batchDelete :: done")
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

    def messages_delete(self, id: str) -> Message:
        """Immediately and permanently deletes the specified message. This operation cannot be undone. Prefer messages.trash instead."""
        api = UsersMessages(self._userId).delete(id)
        self.requests.delete(api, headers=self.config.headers)
        return Message().update_dict(self.requests.to_dict())

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
        logger.info(f"[GoogleGmailClient] :: messages_get :: done")
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
                      labelIds: list = [],
                      includeSpamTrash: bool = False) -> MessageList:
        """Lists the messages in the user's mailbox."""
        logger.debug(
            f"[GoogleGmailClient] :: message_list :: {maxResults=} :: {pageToken=} :: {q=} :: {labelIds=} :: {includeSpamTrash=}")

        if maxResults > 500:
            raise Exception(f"[GoogleGmailClient] :: message_list :: ERROR :: {maxResults=} > 500")

        for label in labelIds:
            if type(label) is Label:
                labelIds = [x.id for x in labelIds]
                break

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

    def messages_list_automon(self, *args, **kwargs) -> MessageList:
        """Enhanced `message_list`"""
        messages = self.messages_list(*args, **kwargs)
        if messages:
            messages = self._improved_messages_list(messages=messages)
        return messages

    def messages_modify(self,
                        id: str,
                        addLabelIds: list = [],
                        removeLabelIds: list = []) -> Message:
        """Modifies the labels on the specified message."""
        if len(addLabelIds) > 100 or len(removeLabelIds) > 100:
            raise Exception(
                f"[GoogleGmailClient] :: messages_modify :: ERROR :: {len(addLabelIds)=} {len(addLabelIds)=} > 100")

        api = UsersMessages(self._userId).modify(id)

        for addLabelId in addLabelIds:
            if type(addLabelId) is Label:
                addLabelIds = [addLabelId.id for addLabelId in addLabelIds]
                break
        for removeLabelId in removeLabelIds:
            if type(removeLabelId) is Label:
                removeLabelIds = [removeLabelId.id for removeLabelId in removeLabelIds]
                break

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

    def messages_trash(self, id: str) -> Message:
        """Moves the specified message to the trash."""
        api = UsersMessages(self._userId).trash(id)
        self.requests.post(api, headers=self.config.headers)
        return Message().update_dict(self.requests.to_dict())

    def messages_untrash(self, id: str):
        """Removes the specified message from the trash."""
        api = UsersMessages(self._userId).untrash(id)
        self.requests.post(api, headers=self.config.headers)
        return self.requests.to_dict()

    def thread_delete(self, id: str) -> Thread:
        api = UsersThread(self._userId).delete(id=id)
        self.requests.delete(api, headers=self.config.headers)
        logger.info(f"[GoogleGmailClient] :: thread_delete :: done")
        return Thread().update_dict(self.requests.to_dict())

    def thread_get(self,
                   id: str,
                   format: Format = Format.full,
                   metadataHeaders: list = None) -> Thread:
        """

        format
        enum (Format)

        The format to return the messages in.

        metadataHeaders[]
        string

        When given and format is METADATA, only include headers specified.
        """
        api = UsersThread(self._userId).get(id=id)
        params = dict(
            format=format,
            metadataHeaders=metadataHeaders
        )
        self.requests.get(api, headers=self.config.headers, params=params)
        logger.info(f"[GoogleGmailClient] :: thread_get :: done")
        return Thread().update_dict(self.requests.to_dict())

    def thread_get_automon(self, *args, **kwargs) -> Thread:

        thread = self.thread_get(*args, **kwargs)
        thread = self._improved_thread_get(thread=thread)

        return thread

    def thread_list(self,
                    q: str = '',
                    maxResults: int = 100,
                    pageToken: str = '',
                    labelIds: list = [],
                    includeSpamTrash: bool = False) -> ThreadList:
        """

        maxResults
        integer (uint32 format)

        Maximum number of threads to return. This field defaults to 100. The maximum allowed value for this field is 500.

        pageToken
        string

        Page token to retrieve a specific page of results in the list.

        q
        string

        Only return threads matching the specified query. Supports the same query format as the Gmail search box. For example, "from:someuser@example.com rfc822msgid:<somemsgid@example.com> is:unread". Parameter cannot be used when accessing the api using the gmail.metadata scope.

        labelIds[]
        string

        Only return threads with labels that match all of the specified label IDs.

        includeSpamTrash
        boolean

        Include threads from SPAM and TRASH in the results.
        """
        for label in labelIds:
            if type(label) is Label:
                labelIds = [x.id for x in labelIds]
                break

        api = UsersThread(self._userId).list
        params = dict(
            maxResults=maxResults,
            pageToken=pageToken,
            q=q,
            labelIds=labelIds,
            includeSpamTrash=includeSpamTrash
        )
        self.requests.get(api, headers=self.config.headers, params=params)
        logger.info(f"[GoogleGmailClient] :: thread_list :: done")
        return ThreadList().update_dict(self.requests.to_dict())

    def thread_list_automon(self, *args, **kwargs) -> ThreadList:
        """Enhanced `thread_list`"""
        threads = self.thread_list(*args, **kwargs)
        if threads:
            threads = self._improved_thread_list(threads=threads)
        logger.info(f"[GoogleGmailClient] :: thread_list_automon :: done")
        return threads

    def thread_modify(self, id: str) -> Thread:
        api = UsersThread(self._userId).modify(id=id)
        self.requests.post(api, headers=self.config.headers)
        logger.info(f"[GoogleGmailClient] :: thread_modify :: done")
        return Thread().update_dict(self.requests.to_dict())

    def thread_trash(self, id: str) -> Thread:
        api = UsersThread(self._userId).trash(id=id)
        self.requests.post(api, headers=self.config.headers)
        logger.info(f"[GoogleGmailClient] :: thread_trash :: done")
        return Thread().update_dict(self.requests.to_dict())

    def thread_untrash(self, id: str):
        api = UsersThread(self._userId).untrash(id=id)
        self.requests.post(api, headers=self.config.headers)
        logger.info(f"[GoogleGmailClient] :: thread_untrash :: done")
        return Thread().update_dict(self.requests.to_dict())

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
