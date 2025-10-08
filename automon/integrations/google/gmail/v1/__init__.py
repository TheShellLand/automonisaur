import io
import re
import bs4
import copy
import json
import base64

from automon.helpers import cryptography
from automon.helpers.loggingWrapper import LoggingClient, INFO

logger = LoggingClient.logging.getLogger(__name__)
logger.setLevel(INFO)


class Api:
    _serviceName = 'gmail'
    _version = 'v1'
    _service_endpoint = 'https://gmail.googleapis.com'

    def __init__(self, service_endpoint: str = None, version: str = None):
        """https://gmail.googleapis.com/gmail/v1"""

        self.url = ''
        if service_endpoint:
            self.url += service_endpoint
        else:
            self.service_endpoint()

        self.gmail()

        if version:
            self.url += version
        else:
            self.version()

    def service_endpoint(self):
        self.url += self._service_endpoint
        return self

    def gmail(self):
        self.url += f'/{self._serviceName}'
        return self

    def version(self):
        self.url += f'/{self._version}'
        return self


class Users(Api):

    def __init__(self, userId: str):
        super().__init__()
        self.userId = userId
        self.users()

    def users(self): self.url += f'/users/{self.userId}'; return self

    @property
    def getProfile(self): """requests.get"""; return self.url + f'/profile'

    @property
    def stop(self): """"requests.post"""; return self.url + f'/stop'

    @property
    def watch(self): """requests.post"""; return self.url + f'/watch'


class UsersDrafts(Users):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def create(self): """requests.post"""; return self.url + f'/drafts'

    def delete(self, id: str): """requests.delete"""; return self.url + f'/drafts/{id}'

    def get(self, id: str): """requests.get"""; return self.url + f'/drafts/{id}'

    @property
    def list(self): """requests.get"""; return self.url + f'/drafts'

    @property
    def send(self): """requests.post"""; return self.url + f'/drafts/send'

    def update(self, id: str): """requests.put"""; return self.url + f'/drafts/{id}'


class UsersHistory(Users):

    def __init__(self, userId: str):
        super().__init__(userId=userId)

    @property
    def list(self): """request.get"""; return self.url + f'/history'


class UsersLabels(Users):

    def __init__(self, userId: str):
        super().__init__(userId=userId)

    @property
    def create(self): """requests.post"""; return self.url + f'/labels'

    @property
    def list(self): """requests.get"""; return self.url + f'/labels'

    def delete(self, id: str): """requests.delete"""; return self.url + f'/labels/{id}'

    def get(self, id: str): """requests.get"""; return self.url + f'/labels/{id}'

    def patch(self, id: str): """requests.get"""; return self.url + f'/labels/{id}'

    def update(self, id: str): """requests.get"""; return self.url + f'/labels/{id}'


class UsersMessages(Users):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def batchDelete(self): """post"""; return self.url + f'/messages/batchDelete'

    @property
    def batchModify(self): """post"""; return self.url + f'/messages/batchModify'

    def delete(self, id: str): """delete"""; return self.url + f'/messages/{id}'

    def get(self, id: str): """get"""; return self.url + f'/messages/{id}'

    @property
    def import_(self): """post"""; return self.url + f'/messages/import'

    @property
    def insert(self): """post"""; return self.url + f'/messages'

    @property
    def list(self): """get"""; return self.url + f'/messages'

    def modify(self, id: str): """post"""; return self.url + f'/messages/{id}/modify'

    @property
    def send(self): """post"""; return self.url + f'/messages/send'

    def trash(self, id: str): """post"""; return self.url + f'/messages/{id}/trash'

    def untrash(self, id: str): """post"""; return self.url + f'/messages/{id}/untrash'


class DictUpdate(dict):

    def __init__(self):
        super().__init__()

    def enhance(self):
        return self

    def __iter__(self):
        return self

    def __repr__(self):
        return f"{self.to_dict()}"

    def get(self, key, *args, **kwargs):
        return self.__dict__.get(key, *args, **kwargs)

    def update_dict(self, update: dict):
        if update is None:
            return self

        if hasattr(update, '__dict__'):
            update = update.__dict__

        for key, value in update.items():
            setattr(self, key, value)

        self.enhance()
        return self

    def update_json(self, json_: str):
        self.update_dict(json.loads(json_))
        return self

    def to_dict(self):
        return self._to_dict(self)

    def _to_dict(self, obj):

        if not hasattr(obj, "__dict__"):
            return obj

        result = {}
        for key, value in obj.__dict__.items():
            if key.startswith("_"):
                continue

            if type(value) is list:
                value = [self._to_dict(x) for x in value]
            else:
                value = self._to_dict(value)

            result[key] = value

        return result


class InternalDateSource:
    receivedTime = 'receivedTime'
    dateHeader = 'dateHeader'


class UsersMessagesAttachments(Users):
    """
    GET https://gmail.googleapis.com/gmail/v1/users/{userId}/messages/{messageId}/attachments/{id}
    """

    def __init__(self, userId: str):
        super().__init__(userId=userId)

    def get(self, messageId: str,
            id: str): """request.get"""; return self.url + f'/messages/{messageId}/attachments/{id}'


class UsersSettings:
    pass


class UsersSettingsCseIdentities:
    pass


class UsersSettingsCseKeypairs:
    pass


class UsersSettingsDelegrates:
    pass


class UsersSettingsFilters:
    pass


class UsersSettingsForwardingAddresses:
    pass


class UsersSettingsSendAs:
    pass


class UsersSettingsSendAsSmimeInfo:
    pass


class LabelListVisibility:
    labelShow = 'labelShow'
    labelHide = 'labelHide'
    labelShowIfUnread = 'labelShowIfUnread'


class AutomonAttachments(DictUpdate):
    attachments: ['MessagePart']

    def __init__(self, attachments: ['MessagePart'] = []):
        super().__init__()

        self.attachments = attachments

    def __repr__(self):
        return f"{len(self.attachments)} attachments"

    def from_hash(self, hash_md5: str):
        for attachment in self.attachments:
            if hash_md5 == attachment.automon_attachment.hash_md5:
                return attachment
        raise Exception(f"[AutomonAttachments] :: from_hash :: hash not found {hash_md5} ::")

    def first_attachment(self) -> 'MessagePart':
        return self.attachments[0]

    def with_filename(self) -> ['MessagePart']:
        return [x for x in self.attachments if x.filename]


class Color(DictUpdate):
    backgroundColor: str
    textColor: str

    """
    JSON representation
    
    {
      "textColor": string,
      "backgroundColor": string
    }
    
    Fields
    textColor	
    string
    
    The text color of the label, represented as hex string. This field is required in order to set the color of a label. Only the following predefined set of color values are allowed:
    #000000, #434343, #666666, #999999, #cccccc, #efefef, #f3f3f3, #ffffff, #fb4c2f, #ffad47, #fad165, #16a766, #43d692, #4a86e8, #a479e2, #f691b3, #f6c5be, #ffe6c7, #fef1d1, #b9e4d0, #c6f3de, #c9daf8, #e4d7f5, #fcdee8, #efa093, #ffd6a2, #fce8b3, #89d3b2, #a0eac9, #a4c2f4, #d0bcf1, #fbc8d9, #e66550, #ffbc6b, #fcda83, #44b984, #68dfa9, #6d9eeb, #b694e8, #f7a7c0, #cc3a21, #eaa041, #f2c960, #149e60, #3dc789, #3c78d8, #8e63ce, #e07798, #ac2b16, #cf8933, #d5ae49, #0b804b, #2a9c68, #285bac, #653e9b, #b65775, #822111, #a46a21, #aa8831, #076239, #1a764d, #1c4587, #41236d, #83334c #464646, #e7e7e7, #0d3472, #b6cff5, #0d3b44, #98d7e4, #3d188e, #e3d7ff, #711a36, #fbd3e0, #8a1c0a, #f2b2a8, #7a2e0b, #ffc8af, #7a4706, #ffdeb5, #594c05, #fbe983, #684e07, #fdedc1, #0b4f30, #b3efd3, #04502e, #a2dcc1, #c2c2c2, #4986e7, #2da2bb, #b99aff, #994a64, #f691b2, #ff7537, #ffad46, #662e37, #ebdbde, #cca6ac, #094228, #42d692, #16a765
    
    backgroundColor	
    string
    
    The background color represented as hex string #RRGGBB (ex #000000). This field is required in order to set the color of a label. Only the following predefined set of color values are allowed:
    #000000, #434343, #666666, #999999, #cccccc, #efefef, #f3f3f3, #ffffff, #fb4c2f, #ffad47, #fad165, #16a766, #43d692, #4a86e8, #a479e2, #f691b3, #f6c5be, #ffe6c7, #fef1d1, #b9e4d0, #c6f3de, #c9daf8, #e4d7f5, #fcdee8, #efa093, #ffd6a2, #fce8b3, #89d3b2, #a0eac9, #a4c2f4, #d0bcf1, #fbc8d9, #e66550, #ffbc6b, #fcda83, #44b984, #68dfa9, #6d9eeb, #b694e8, #f7a7c0, #cc3a21, #eaa041, #f2c960, #149e60, #3dc789, #3c78d8, #8e63ce, #e07798, #ac2b16, #cf8933, #d5ae49, #0b804b, #2a9c68, #285bac, #653e9b, #b65775, #822111, #a46a21, #aa8831, #076239, #1a764d, #1c4587, #41236d, #83334c #464646, #e7e7e7, #0d3472, #b6cff5, #0d3b44, #98d7e4, #3d188e, #e3d7ff, #711a36, #fbd3e0, #8a1c0a, #f2b2a8, #7a2e0b, #ffc8af, #7a4706, #ffdeb5, #594c05, #fbe983, #684e07, #fdedc1, #0b4f30, #b3efd3, #04502e, #a2dcc1, #c2c2c2, #4986e7, #2da2bb, #b99aff, #994a64, #f691b2, #ff7537, #ffad46, #662e37, #ebdbde, #cca6ac, #094228, #42d692, #16a765
    """

    def __init__(self, backgroundColor: str = None, textColor: str = None):
        super().__init__()
        self.backgroundColor = backgroundColor
        self.textColor = textColor

    def __bool__(self):
        if self.backgroundColor and self.textColor:
            return True
        return False


class Draft(DictUpdate):
    id: str
    message: 'Message'
    """
    A draft email in the user's mailbox.
    
    {
      "message": {
        "raw": "string"
      }
    }
    

    JSON representation
    
    {
      "id": string,
      "message": {
        object (Message)
      }
    }
    Fields
    id	
    string
    
    The immutable ID of the draft.
    
    message	
    object (Message)
    
    The message content of the draft.
    """

    def __init__(self, id: str = None, message: 'Message' = None):
        super().__init__()

        self.id = id
        self.message = message

    def enhance(self):
        if hasattr(self, 'message'):
            if self.message is not None:
                setattr(self, 'message', Message().update_dict(self.message))

    def __repr__(self):
        try:
            return f'{self.id} :: {self.message.automon_subject().value}'
        except:
            return f"{self.id}"


class DraftList(DictUpdate):
    drafts: list
    nextPageToken: str
    resultSizeEstimate: int

    """
    If successful, the response body contains data with the following structure:

    JSON representation
    
    {
      "drafts": [
        {
          object (Draft)
        }
      ],
      "nextPageToken": string,
      "resultSizeEstimate": integer
    }
    Fields
    drafts[]	
    object (Draft)
    
    List of drafts. Note that the Message property in each Draft resource only contains an id and a threadId. The messages.get method can fetch additional message details.
    
    nextPageToken	
    string
    
    Token to retrieve the next page of results in the list.
    
    resultSizeEstimate	
    integer (uint32 format)
    
    Estimated total number of results.
    """

    def __init__(self):
        super().__init__()

    def __repr__(self):
        if hasattr(self, 'drafts'):
            return f"{len(self.drafts)} drafts"


class EmailAttachment(DictUpdate):
    filename: str
    bytes_: bytes
    mimeType: str
    content_type: str
    encoding: str

    def __init__(self,
                 bytes_: bytes,
                 filename: str = '',
                 mimeType: str = None,
                 content_type: str = None,
                 encoding: str = None):
        super().__init__()

        if type(bytes_) is not bytes:
            raise Exception(f"Not bytes")

        self.bytes_ = bytes_
        self.filename = filename
        self.mimeType = mimeType

        if mimeType:
            self.content_type, self.encoding = mimeType.split('/', 1)
        elif content_type and encoding:
            self.content_type = content_type
            self.encoding = encoding

    def __bool__(self):
        if self.bytes_:
            return True
        return False


class Format:
    minimal = 'minimal'
    full = 'full'
    raw = 'raw'
    metadata = 'metadata'


class GmailLabels:

    def __init__(self):
        self.draft = Label(name='DRAFT', id='DRAFT')
        self.sent = Label(name='SENT', id='SENT')
        self.unread = Label(name='UNREAD', id='UNREAD')
        self.trash = Label(name='TRASH', id='TRASH')


class Headers(DictUpdate):
    name: str
    value: str

    def __init__(self):
        super().__init__()

        self.name = ''
        self.value = ''

    def __repr__(self):
        if self.name:
            return f"{self.name} :: {self.value}"

    def __eq__(self, other):
        if self.name == other.name and self.value == other.value:
            return True
        return False

    def __lt__(self, other):
        return self.name < other.name


class HistoryType(DictUpdate):
    id: str
    messages: 'Message'
    messagesAdded: 'MessageAdded'
    messagesDeleted: 'MessageDeleted'
    labelsAdded: 'LabelAdded'
    labelsRemoved: 'LabelRemoved'

    """
    {
      "id": string,
      "messages": [
        {
          object (Message)
        }
      ],
      "messagesAdded": [
        {
          object (MessageAdded)
        }
      ],
      "messagesDeleted": [
        {
          object (MessageDeleted)
        }
      ],
      "labelsAdded": [
        {
          object (LabelAdded)
        }
      ],
      "labelsRemoved": [
        {
          object (LabelRemoved)
        }
      ]
    }
    """

    def __init__(self):
        super().__init__()


class MessageListVisibility:
    show = 'show'
    hide = 'hide'


class Label(DictUpdate):
    id: str
    name: str
    messageListVisibility: MessageListVisibility
    labelListVisibility: LabelListVisibility
    type: 'Type'
    messagesTotal: int
    messagesUnread: int
    threadsTotal: int
    threadsUnread: int
    color: Color

    """
    {
      "id": string,
      "name": string,
      "messageListVisibility": enum (MessageListVisibility),
      "labelListVisibility": enum (LabelListVisibility),
      "type": enum (Type),
      "messagesTotal": integer,
      "messagesUnread": integer,
      "threadsTotal": integer,
      "threadsUnread": integer,
      "color": {
        object (Color)
      }
    }

    Fields
    id	
    string

    The immutable ID of the label.

    name	
    string

    The display name of the label.

    messageListVisibility	
    enum (MessageListVisibility)

    The visibility of messages with this label in the message list in the Gmail web interface.

    labelListVisibility	
    enum (LabelListVisibility)

    The visibility of the label in the label list in the Gmail web interface.

    type	
    enum (Type)

    The owner type for the label. User labels are created by the user and can be modified and deleted by the user and can be applied to any message or thread. System labels are internally created and cannot be added, modified, or deleted. System labels may be able to be applied to or removed from messages and threads under some circumstances but this is not guaranteed. For example, users can apply and remove the INBOX and UNREAD labels from messages and threads, but cannot apply or remove the DRAFTS or SENT labels from messages or threads.

    messagesTotal	
    integer

    The total number of messages with the label.

    messagesUnread	
    integer

    The number of unread messages with the label.

    threadsTotal	
    integer

    The total number of threads with the label.

    threadsUnread	
    integer

    The number of unread threads with the label.

    color	
    object (Color)

    The color to assign to the label. Color is only available for labels that have their type set to user.
    """

    def __init__(self, id: str = None, name: str = None, color: Color = None,
                 messageListVisibility: MessageListVisibility = MessageListVisibility.show,
                 labelListVisibility: LabelListVisibility = LabelListVisibility.labelShow):
        super().__init__()
        self.id = id
        self.name = name
        self.color = color
        self.messageListVisibility = messageListVisibility
        self.labelListVisibility = labelListVisibility

    def __repr__(self):
        if self.id and self.name:
            return f"{self.id} :: {self.name}"
        return str(self.id)

    def __eq__(self, other):
        if self.id == other.id and self.name == other.name:
            return True
        return False

    def enhance(self):
        if hasattr(self, 'color'):
            self.color = Color().update_dict(self.color)


class LabelList(DictUpdate):
    labels: [Label]

    def __init__(self):
        super().__init__()
        self.labels = []

    def enhance(self):
        if hasattr(self, 'labels'):
            setattr(self, 'labels', [Label().update_dict(x) for x in self.labels])


class LabelAdded:
    pass


class LabelRemoved:
    pass


class Message(DictUpdate):
    id: str
    threadId: str
    labelIds: [str]
    snippet: str
    historyId: str
    internalDate: str
    payload: 'MessagePart'
    sizeEstimate: str
    raw: str

    automon_labels: ['Label']
    automon_subject: Headers
    automon_to: Headers
    automon_from: Headers
    automon_to_email: str
    automon_from_email: str
    automon_subject: Headers
    automon_raw_decoded: str
    automon_attachments: AutomonAttachments

    """
    {
      "id": string,
      "threadId": string,
      "labelIds": [
        string
      ],
      "snippet": string,
      "historyId": string,
      "internalDate": string,
      "payload": {
        object (MessagePart)
      },
      "sizeEstimate": integer,
      "raw": string
    }


    Fields
    id
    string

    The immutable ID of the message.

    threadId
    string

    The ID of the thread the message belongs to. To add a message or draft to a thread, the following criteria must be met:

    The requested threadId must be specified on the Message or Draft.Message you supply with your request.
    The References and In-Reply-To headers must be set in compliance with the RFC 2822 standard.
    The Subject headers must match.

    labelIds[]
    string

    List of IDs of labels applied to this message.

    snippet
    string

    A short part of the message text.

    historyId
    string

    The ID of the last history record that modified this message.

    internalDate
    string (int64 format)

    The internal message creation timestamp (epoch ms), which determines ordering in the inbox. For normal SMTP-received email, this represents the time the message was originally accepted by Google, which is more reliable than the Date header. However, for API-migrated mail, it can be configured by client to be based on the Date header.

    payload
    object (MessagePart)

    The parsed email structure in the message parts.

    sizeEstimate
    integer

    Estimated size in bytes of the message.

    raw
    string (bytes format)

    The entire email message in an RFC 2822 formatted and base64url encoded string. Returned in messages.get and drafts.get responses when the format=RAW parameter is supplied.

    A base64-encoded string.
    """

    def __init__(self, id: str = None, threadId: str = None, raw: str = None):
        super().__init__()

        self.id = id
        self.threadId = threadId
        self.raw = raw

        self.automon_labels = []

    def __bool__(self):
        if self.id:
            return True
        return False

    def __eq__(self, other):
        if self.id == other.id:
            return True
        return False

    def enhance(self):

        if hasattr(self, 'payload'):
            setattr(self, 'payload', MessagePart().update_dict(self.payload))

        return self

    def automon_from(self) -> Headers:
        if hasattr(self, 'payload'):
            if hasattr(self.payload, 'headers'):

                for header in self.payload.headers:
                    if header.name == 'From':
                        return header
        return Headers()

    @property
    def automon_from_email(self) -> str:
        email_re = r"(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|\"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*\")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])"
        email_re = re.compile(email_re, flags=re.IGNORECASE)
        email = email_re.search(self.automon_from().value).group()

        return email

    @property
    def automon_subject(self):
        if hasattr(self, 'payload'):
            if hasattr(self.payload, 'headers'):

                for header in self.payload.headers:
                    if header.name == 'Subject':
                        return header
        return Headers()

    def automon_to(self):
        if hasattr(self, 'payload'):
            if hasattr(self.payload, 'headers'):

                for header in self.payload.headers:
                    if header.name == 'To':
                        return header
        return Headers()

    @property
    def automon_to_email(self) -> str:
        email_re = r"(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|\"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*\")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])"
        email_re = re.compile(email_re, flags=re.IGNORECASE)
        email = email_re.search(self.automon_to().value).group()

        return email

    def automon_raw_decoded(self):
        if self.raw is not None:
            return base64.urlsafe_b64decode(self.raw).decode()

    @property
    def automon_attachments(self) -> AutomonAttachments:
        if hasattr(self, 'payload'):
            if hasattr(self.payload, 'automon_attachments'):
                return self.payload.automon_attachments()
            else:
                return AutomonAttachments(attachments=[self.payload])

    def __repr__(self):
        if hasattr(self, 'snippet'):
            return self.snippet
        return ''


class MessagePartBody(DictUpdate):
    attachmentId: str
    size: int
    data: str

    """
    {
      "attachmentId": string,
      "size": integer,
      "data": string
    }
    """

    def __init__(self):
        super().__init__()

        self.attachmentId = ''

    def enhance(self):

        if hasattr(self, 'data'):
            setattr(self, 'automon_data_BytesIO', io.BytesIO(self.automon_data_base64decoded()))
            setattr(self, 'automon_data_html_text', self._html_text())

    def automon_data_base64decoded(self):
        if hasattr(self, 'data'):
            return base64.urlsafe_b64decode(self.data)

    def automon_data_decoded(self):
        if hasattr(self, 'data'):
            try:
                return self.automon_data_base64decoded().decode()
            except Exception as error:
                pass

    def automon_data_hash(self):
        if hasattr(self, 'data'):
            try:
                return setattr(self, 'automon_data_hash', cryptography.Hashlib.md5(self.automon_data_decoded()))
            except Exception as error:
                pass

    def __repr__(self):
        return f"{self.attachmentId}"

    def automon_data_bs4(self):
        if hasattr(self, 'automon_data_base64decoded'):
            return bs4.BeautifulSoup(self.automon_data_base64decoded())

    def _html_text(self):
        try:
            return self.automon_data_bs4().html.text
        except:
            return None


class MessagePart(DictUpdate):
    partId: str
    mimeType: str
    filename: str
    headers: ['Headers']
    body: MessagePartBody
    parts: ['MessagePart']

    """
    A single MIME message part.

    JSON representation

    {
      "partId": string,
      "mimeType": string,
      "filename": string,
      "headers": [
        {
          object (Header)
        }
      ],
      "body": {
        object (MessagePartBody)
      },
      "parts": [
        {
          object (MessagePart)
        }
      ]
    }

    Fields
    partId
    string

    The immutable ID of the message part.

    mimeType
    string

    The MIME type of the message part.

    filename
    string

    The filename of the attachment. Only present if this message part represents an attachment.

    headers[]
    object (Header)

    List of headers on this message part. For the top-level message part, representing the entire message payload, it will contain the standard RFC 2822 email headers such as To, From, and Subject.

    body
    object (MessagePartBody)

    The message part body for this part, which may be empty for container MIME message parts.

    parts[]
    object (MessagePart)

    The child MIME message parts of this part. This only applies to container MIME message parts, for example multipart/*. For non- container MIME message part types, such as text/plain, this field is empty. For more information, see RFC 1521.
    """

    def __init__(self):
        super().__init__()

        self.headers = []

    def enhance(self):

        if hasattr(self, 'body'):
            setattr(self, 'body', MessagePartBody().update_dict(self.body))

        if hasattr(self, 'headers'):
            setattr(self, 'headers', [Headers().update_dict(x) for x in self.headers])

        if hasattr(self, 'parts'):
            setattr(self, 'parts', [MessagePart().update_dict(x) for x in self.parts])

        return self

    def automon_attachments(self) -> AutomonAttachments:
        if hasattr(self, 'parts'):
            return AutomonAttachments(attachments=self.parts)
        return AutomonAttachments()

    def get_header(self, header: str) -> Headers:
        for _header in self.headers:
            if header.lower() in _header.name.lower():
                return _header

    def __repr__(self):
        if getattr(self, 'filename') and getattr(self, 'mimeType'):
            return f"{self.filename} :: {self.mimeType}"
        elif getattr(self, 'mimeType'):
            return f"{self.mimeType}"


class MessageAdded:
    pass


class MessageDeleted:
    pass


class MessageList(DictUpdate):
    messages: [Message]
    resultSizeEstimate: int
    nextPageToken: str

    """
    {
      "messages": [
        {
          object (Message)
        }
      ],
      "nextPageToken": string,
      "resultSizeEstimate": integer
    }
    """

    def __init__(self):
        super().__init__()

        self.messages = []

    def __bool__(self):
        if hasattr(self, 'messages'):
            return True
        return False

    def enhance(self):
        if hasattr(self, 'messages'):
            setattr(self, 'messages', [Message().update_dict(message) for message in self.messages])

        return self

    def __repr__(self):
        if hasattr(self, 'messages'):
            return f'{len(self.messages)} messages'


class Thread(DictUpdate):
    id: str
    snippet: str
    historyId: str
    messages: [Message]

    addLabelIds: list
    removeLabelIds: list

    """
    A collection of messages representing a conversation.

    {
      "id": string,
      "snippet": string,
      "historyId": string,
      "messages": [
        {
          object (Message)
        }
      ]
    }
    """

    def __init__(self):
        super().__init__()
        self.id: str = ''
        self.historyId: str = ''
        self.messages: [Message] = []
        self.snippet: str = ''

        self.addLabelIds: list = []
        self.removeLabelIds: list = []

    def __repr__(self):
        if self.snippet:
            return self.snippet

        if self.id and self.automon_messages_count:
            return f'{self.id} :: {self.automon_messages_count} messages'

        return f'{self}'

    def __bool__(self):
        if self.messages:
            return True
        return False

    @property
    def automon_clean_thread(self):
        """Return a clean list of messages not labeled with TRASH"""
        messages = []
        labels = GmailLabels()

        if self.messages:
            for message in self.messages:
                if labels.trash not in message.automon_labels:
                    messages.append(message)

        thread_copy = copy.deepcopy(self)
        thread_copy.messages = messages
        return thread_copy

    @property
    def automon_clean_thread_first(self) -> Message:
        if self.automon_clean_thread.messages:
            return self.automon_clean_thread.messages[0]

    @property
    def automon_clean_thread_latest(self) -> Message:
        if self.automon_clean_thread.messages:
            return self.automon_clean_thread.messages[-1]

    @property
    def automon_full_thread(self):
        """Return the full thread including TRASH messages"""
        messages = []
        labels = GmailLabels()

        if self.messages:
            for message in self.messages:
                if labels.draft not in message.automon_labels:
                    messages.append(message)

        thread_copy = copy.deepcopy(self)
        thread_copy.messages = messages
        return thread_copy

    @property
    def automon_full_thread_first(self) -> Message:
        if self.automon_full_thread.messages:
            return self.automon_full_thread.messages[0]

    @property
    def automon_full_thread_latest(self) -> Message:
        if self.automon_full_thread.messages:
            return self.automon_full_thread.messages[-1]

    @property
    def automon_messages_count(self):
        return len(self.messages)

    @property
    def automon_message_first(self) -> Message:
        if self.messages:
            return self.messages[0]

    @property
    def automon_message_latest(self) -> Message:
        if self.messages:
            return self.messages[-1]

    def enhance(self):
        if self.messages:
            self.messages = [Message().update_dict(x) for x in self.messages]

        return self


class ThreadList(DictUpdate):
    threads: [Thread]
    nextPageToken: str
    resultSizeEstimate: int

    """
    {
      "threads": [
        {
          object (Thread)
        }
      ],
      "nextPageToken": string,
      "resultSizeEstimate": integer
    }
    """

    def __init__(self):
        super().__init__()

        self.threads: [Thread] = []
        self.nextPageToken = ''
        self.resultSizeEstimate = None

    def __bool__(self):
        if hasattr(self, 'threads'):
            return True
        return False

    def enhance(self):
        if hasattr(self, 'threads'):
            self.threads = [Thread().update_dict(x) for x in self.threads]

    def __repr__(self):
        if hasattr(self, 'threads'):
            return f"{len(self.threads)} threads"


class Type:
    system = 'system'
    user = 'user'


class UsersThread(Users):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def delete(self, id: str): """requests.delete"""; return self.url + f'/threads/{id}'

    def get(self, id: str): """requests.get"""; return self.url + f'/threads/{id}'

    @property
    def list(self): """requests.get"""; return self.url + f'/threads'

    def modify(self, id: str):
        """Modifies the labels applied to the thread. This applies to all messages in the thread.

        requests.post
        """
        return self.url + f'/threads/{id}/modify'

    def trash(self, id: str): """requests.post"""; return self.url + f'/threads/{id}/trash'

    def untrash(self, id: str): """reqiests.post"""; return self.url + f'/threads/{id}/untrash'
