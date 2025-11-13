import io
import re
import bs4
import copy
import json
import base64
import datetime
import dateutil.parser

try:
    from typing import Self
except:
    from typing_extensions import Self

from automon.helpers import cryptography
from automon.helpers.dictWrapper import DictUpdate
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


class EmailAttachment(DictUpdate):

    def __init__(self,
                 bytes_: bytes,
                 filename: str = '',
                 mimeType: str = None,
                 content_type: str = None,
                 encoding: str = None):
        super().__init__()

        if type(bytes_) is not bytes:
            raise Exception(f"Not bytes")

        self.bytes_: bytes = bytes_
        self.filename: str = filename
        self.mimeType: str = mimeType
        self.content_type: str = None
        self.encoding: str = None

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


class Header(DictUpdate):

    def __init__(self, header: dict | Self = None):
        super().__init__()

        self.name: str = ''
        self.value: str = ''

        if header:
            self._update(header)

    def __repr__(self):
        if self.name:
            return f"{self.name} :: {self.value}"

    def __bool__(self):
        if self.value:
            return True
        return False

    def __eq__(self, other):
        if self.name == other.name and self.value == other.value:
            return True
        return False

    def __lt__(self, other):
        return self.name < other.name


class HistoryType(DictUpdate):
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

        self.id: str
        self.messages: Message = None
        self.messagesAdded: MessageAdded = None
        self.messagesDeleted: MessageDeleted = None
        self.labelsAdded: LabelAdded = None
        self.labelsRemoved: LabelRemoved = None


class MessageListVisibility:
    show = 'show'
    hide = 'hide'


class Type:
    system: str = 'system'
    user: str = 'user'


class Label(DictUpdate):
    id: str
    name: str
    messageListVisibility: MessageListVisibility
    labelListVisibility: LabelListVisibility
    type: Type
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
        if self.name:
            return f"{self.name}"
        return str(self.id)

    def __eq__(self, other):
        if self.id == other.id and self.name == other.name:
            return True
        return False

    def _enhance(self):
        if hasattr(self, 'color'):
            self.color = Color()._update(self.color)


class LabelList(DictUpdate):
    labels: list[Label]

    def __init__(self, labels: dict = None):
        super().__init__()
        self.labels: list[Label] = []

        if labels:
            self._update(labels)

    def _enhance(self):
        if self.labels:
            self.labels = [Label()._update(x) for x in self.labels]


class LabelAdded:
    pass


class LabelRemoved:
    pass


class MessagePartBody(DictUpdate):
    """
    {
      "attachmentId": string,
      "size": integer,
      "data": string
    }
    """

    def __init__(self, message: dict | Self = None):
        super().__init__()

        self.attachmentId: str = None
        self.size: int = None
        self.data: str = None

        if message:
            self._update(message)

    def __repr__(self):
        repr = []

        if self.attachmentId:
            repr.append(self.attachmentId[-8:])

        if self.automon_data_hash:
            repr.append(self.automon_data_hash)

        if self.size:
            repr.append(f'{self.size} B')

        return ' :: '.join(repr)

    def __bool__(self):
        if self.size > 0:
            return True
        if self.data:
            return True
        if self.attachmentId:
            return True
        return False

    def automon_data_base64decoded(self) -> bytes | None:
        if self.data:
            return base64.urlsafe_b64decode(self.data)

    def automon_data_BytesIO(self) -> io.BytesIO | None:
        if self.data:
            return io.BytesIO(self.automon_data_base64decoded())

    def automon_data_html_text(self) -> str | None:
        if self.data:
            return self._html_text()

    def automon_data_decoded(self) -> str | None:
        if self.data:
            try:
                return self.automon_data_base64decoded().decode()
            except Exception as error:
                pass

    @property
    def automon_data_hash(self):
        if self.data:
            return cryptography.Hashlib.md5(self.data)

    def automon_data_bs4(self) -> bs4.BeautifulSoup | None:
        decoded = self.automon_data_base64decoded()
        if decoded:
            return bs4.BeautifulSoup(decoded)

    def _html_text(self) -> str | None:
        if self.automon_data_bs4():
            return self.automon_data_bs4().html.text


class MessagePart(DictUpdate):
    partId: str
    mimeType: str
    filename: str
    headers: list[dict]
    body: dict

    parts: list[dict]

    automon_body: MessagePartBody
    automon_headers: list[Header]
    automon_parts: list[Self]

    def __init__(self, part: dict | Self = None):
        super().__init__()

        self.partId: str = ''
        self.mimeType: str = ''
        self.filename: str = ''
        self.headers: list[str] = []
        self.body: dict = {}

        self.parts: list[dict] = []

        if part:
            self._update(part)

    def __repr__(self):
        repr = []

        if self.filename:
            repr.append(self.filename)

        if self.mimeType:
            repr.append(self.mimeType)

        return ' :: '.join(repr)

    @property
    def automon_body(self) -> MessagePartBody | None:
        if self.body:
            return MessagePartBody(self.body)

    @property
    def automon_headers(self) -> list[Header] | None:
        if self.headers:
            return [Header(x) for x in self.headers]

    @property
    def automon_parts(self) -> list[Self] | None:
        if self.parts:
            return [MessagePart(x) for x in self.parts]

    def get_header(self, header: str) -> Header | None:
        for headers in self.automon_headers:
            if header.lower() in headers.name.lower():
                return headers


class MessagePayload(DictUpdate):
    partId: str
    mimeType: str
    filename: str
    headers: list[str]
    body: dict

    parts: list[dict]
    size: int

    automon_body: MessagePartBody
    automon_headers: list[Header]
    automon_parts: list[MessagePart]

    def __init__(self, message: dict | Self = None):
        super().__init__()

        self.parts: list[dict] = []
        self.size: int = None

        if message:
            self._update(message)

    def __repr__(self):
        repr = []

        if self.filename:
            repr.append(self.filename)

        if self.mimeType:
            repr.append(self.mimeType)

        if self.size:
            repr.append(f"{self.size} B")

        return ' :: '.join(repr)

    def __bool__(self):
        if self.size is not None and self.size > 0:
            return True
        if self.automon_parts:
            return True
        if self.automon_body:
            return True
        return False

    @property
    def automon_body(self) -> MessagePartBody | None:
        if self.body:
            return MessagePartBody(self.body)

    @property
    def automon_headers(self) -> list[Header] | None:
        if self.headers:
            return [Header(x) for x in self.headers]

    @property
    def automon_parts(self) -> list[MessagePart]:
        if self.parts:
            return [MessagePart(x) for x in self.parts]
        return []

    def get_header(self, header: str) -> Header | None:
        for headers in self.automon_headers:
            if header.lower() in headers.name.lower():
                return headers


class Message(DictUpdate):
    historyId: str
    id: str
    internalDate: str
    labelIds: list[str]
    payload: dict
    raw: str
    sizeEstimate: str
    snippet: str
    threadId: str

    automon_attachments: list
    automon_date: dateutil.parser.parse
    automon_date_since_now: datetime.timedelta
    automon_date_since_now_str: str
    automon_email_from: str
    automon_email_to: str
    automon_header_from: Header
    automon_header_subject: Header
    automon_header_to: Header
    automon_labels: list[Label] = []
    automon_payload: MessagePayload
    automon_raw_decoded: str

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

    def __init__(self, message: dict = None):
        super().__init__()

        self.historyId: str = None
        self.id: str = None
        self.internalDate: str = None
        self.labelIds: list[str] = []
        self.payload: dict = None
        self.raw: str = None
        self.sizeEstimate: str = None
        self.snippet: str = None
        self.threadId: str = None

        self.automon_labels: list[Label] = []

        if message:
            self._update(message)

    def __repr__(self):
        if self.snippet:
            return self.snippet
        return self.id

    def __bool__(self):
        if self.id:
            return True
        return False

    def __eq__(self, other):
        if self.id == other.id:
            return True
        return False

    @property
    def automon_attachments(self) -> list[MessagePartBody | MessagePart] | None:
        if self.automon_payload:
            if self.automon_payload.size:
                return [self.automon_payload.automon_body]
            if self.automon_payload.automon_parts:
                return self.automon_payload.automon_parts

    @property
    def automon_attachments_first(self) -> MessagePartBody | MessagePart | None:
        if self.automon_attachments:
            return self.automon_attachments[0]

    @property
    def automon_date(self) -> dateutil.parser.parse:
        if self.automon_payload:
            header = self.automon_payload.get_header('Date')
            if header:
                return dateutil.parser.parse(header.value)

    @property
    def automon_date_since_now(self) -> datetime.timedelta | None:
        if self.automon_date:
            automon_date = self.automon_date
            time_delta = datetime.datetime.now() + automon_date.utcoffset()
            time_delta = time_delta.replace(tzinfo=datetime.timezone(automon_date.utcoffset()))
            time_delta = time_delta - automon_date

            return time_delta

    @property
    def automon_date_since_now_str(self) -> str | None:
        if self.automon_date_since_now:
            time_delta = self.automon_date_since_now

            days = time_delta.days
            if days > 0:
                return f"{days} days ago"

            hours = time_delta.seconds // 3600
            if hours > 0:
                return f"{hours} hours ago"

            minutes = time_delta.seconds // 60
            if minutes > 0:
                return f"{minutes} minutes ago"

            seconds = time_delta.seconds % 60
            if seconds > 0:
                return f"{seconds} seconds ago"

    @property
    def automon_email_from(self) -> str | None:
        automon_header_from = self.automon_header_from
        if automon_header_from:
            email_re = r"(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|\"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*\")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])"
            email_re = re.compile(email_re, flags=re.IGNORECASE)
            email = email_re.search(automon_header_from.value).group()

            return email

    @property
    def automon_email_to(self) -> str | None:
        automon_header_to = self.automon_header_to
        if automon_header_to:
            email_re = r"(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|\"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*\")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])"
            email_re = re.compile(email_re, flags=re.IGNORECASE)
            email = email_re.search(automon_header_to.value).group()

            return email

    @property
    def automon_header_from(self) -> Header | None:
        if self.automon_payload:
            if self.automon_payload.automon_headers:
                return self.automon_payload.get_header('From')

    @property
    def automon_header_subject(self) -> Header | None:
        if self.automon_payload:
            if self.automon_payload.automon_headers:
                return self.automon_payload.get_header('Subject')

    @property
    def automon_header_to(self) -> Header | None:
        if self.automon_payload:
            if self.automon_payload.automon_headers:
                return self.automon_payload.get_header('To')

    @property
    def automon_payload(self) -> MessagePayload | None:
        if self.payload:
            return MessagePayload(self.payload)

    def automon_raw_decoded(self) -> str | None:
        if self.raw is not None:
            return base64.urlsafe_b64decode(self.raw).decode()


class MessageAttachments(DictUpdate):

    def __init__(self, attachments: list[dict] = []):
        super().__init__()

        self.attachments: list[dict] = attachments

    def __repr__(self):
        return f"{len(self.attachments)} attachments"

    def __bool__(self):
        if self.attachments:
            return True
        return False

    @property
    def automon_attachments(self) -> list[MessagePart] | None:
        return [MessagePart(x) for x in self.attachments]

    @property
    def automon_first_attachment(self) -> MessagePart | None:
        for part in self.automon_attachments:
            return part

    def from_hash(self, hash_md5: str):
        for attachment in self.automon_attachments:
            if hash_md5 == attachment.automon_attachment.hash_md5:
                return attachment
        raise Exception(f"[AutomonAttachments] :: from_hash :: hash not found {hash_md5} ::")

    @property
    def has_filename(self) -> list[MessagePart]:
        return [x for x in self.automon_attachments if x.filename]


class MessageAdded:
    pass


class MessageDeleted:
    pass


class MessageList(DictUpdate):
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

    def __init__(self, messages: dict | Self = None):
        super().__init__()

        self.messages: list = []
        self.resultSizeEstimate: int
        self.nextPageToken: str

        self._automon_messages = []

        if messages:
            self._update(messages)

    def __repr__(self):
        if self.messages:
            return f'{len(self.messages)} messages'
        return ''

    def __bool__(self):
        if self.messages:
            return True
        return False

    @property
    def automon_messages(self) -> list[Message] | list:
        if self.messages and not self._automon_messages:
            self._automon_messages = [Message(message) for message in self.messages]
        return self._automon_messages


class Draft(DictUpdate):
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

    def __init__(self, id: str = None, message: Message = None):
        super().__init__()

        self.id: str = id
        self.message: Message = message

    @property
    def automon_message(self) -> Message | None:
        if self.message:
            return Message(self.message)

    def __repr__(self):
        try:
            return f'{self.id} :: {self.message.automon_header_subject.value}'
        except:
            return f"{self.id}"


class DraftList(DictUpdate):
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

        self.drafts: list = []
        self.nextPageToken: str = None
        self.resultSizeEstimate: int = None

    def __repr__(self):
        if self.drafts:
            return f"{len(self.drafts)} drafts"
        return str(self)


class Thread(DictUpdate):
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

    def __init__(self, thread: dict | Self = None):
        super().__init__()
        self.id: str = ''
        self.historyId: str = ''
        self.messages: list = []
        self.snippet: str = ''

        self.addLabelIds: list = []
        self.removeLabelIds: list = []

        self._automon_messages: list[Message] = []

        if thread:
            self._update(thread)

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
    def automon_messages(self) -> list[Message] | None:
        if self.messages and not self._automon_messages:
            self._automon_messages = [Message(x) for x in self.messages]
        return self._automon_messages

    @property
    def automon_messages_count(self) -> int:
        return len(self.automon_messages)

    @property
    def automon_clean_thread(self) -> Self:
        """Return a clean list of messages not labeled with TRASH or DRAFT"""
        messages = []
        labels = GmailLabels()

        if self.automon_messages:
            for message in self.automon_messages:
                if labels.trash not in message.automon_labels:
                    if labels.draft not in message.automon_labesl:
                        messages.append(message)

        thread_copy = copy.deepcopy(self)
        thread_copy.messages = messages
        return messages

    @property
    def automon_clean_thread_first(self) -> Message | None:
        if self.automon_clean_thread:
            return self.automon_clean_thread[0]

    @property
    def automon_clean_thread_latest(self) -> Message | None:
        if self.automon_clean_thread:
            return self.automon_clean_thread[-1]

    @property
    def automon_full_thread(self) -> Self:
        """Return the full thread including TRASH messages"""
        messages = []
        labels = GmailLabels()

        if self.automon_messages:
            for message in self.automon_messages:
                if labels.draft not in message.automon_labels:
                    messages.append(message)

        thread_copy = copy.deepcopy(self)
        thread_copy.messages = messages
        return messages

    @property
    def automon_full_thread_first(self) -> Message | None:
        if self.automon_full_thread:
            return self.automon_full_thread[0]

    @property
    def automon_full_thread_latest(self) -> Message | None:
        if self.automon_full_thread:
            return self.automon_full_thread[-1]

    @property
    def automon_messages_count(self):
        return len(self.automon_messages)

    @property
    def automon_message_first(self) -> Message | None:
        if self.automon_messages:
            return self.automon_messages[0]

    @property
    def automon_message_latest(self) -> Message | None:
        if self.automon_messages:
            return self.automon_messages[-1]


class ThreadList(DictUpdate):
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

    def __init__(self, threads: dict | Self = None):
        super().__init__()

        self.threads: list = []
        self.nextPageToken: str = None
        self.resultSizeEstimate: int = None

        self._automon_threads = []

        if threads:
            self._update(threads)

    def __repr__(self):
        return f"{len(self.threads)} threads"

    def __bool__(self) -> bool:
        if self.threads:
            return True
        return False

    @property
    def automon_threads(self) -> list[Thread]:
        if self.threads and not self._automon_threads:
            self._automon_threads = [Thread(x) for x in self.threads]
        return self._automon_threads


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
