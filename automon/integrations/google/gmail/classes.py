import io
import bs4
import base64
import datetime
import hashlib
import dateutil.parser

from typing import Self

from automon.helpers import *
from automon.helpers.loggingWrapper import LoggingClient, INFO

logger = LoggingClient.logging.getLogger(__name__)
logger.setLevel(INFO)


class AutomonLabels:

    def __init__(self):
        self._reset_labels = False

        self._color_default = Color(backgroundColor='#653e9b', textColor='#e4d7f5')
        self._color_debug = Color(backgroundColor='#cc3a21', textColor='#ffd6a2')
        self._color_error = Color(backgroundColor='#cc3a21', textColor='#ffd6a2')
        self._color_green = Color(backgroundColor='#076239', textColor='#b9e4d0')
        self._color_light = Color(backgroundColor='#8e63ce', textColor='#ffffff')
        self._color_pink = Color(backgroundColor='#b65775', textColor='#ffffff')
        self._color_yellow = Color(backgroundColor='#ffbc6b', textColor='#fef1d1')

        # general
        self.draft = Label(name='DRAFT', id='DRAFT')
        self.sent = Label(name='SENT', id='SENT')
        self.unread = Label(name='UNREAD', id='UNREAD')
        self.trash = Label(name='TRASH', id='TRASH')

        # required
        self.automon = Label(name='automon', color=self._color_default)

        # resume
        self.resume = Label(name='automon/resume', color=self._color_light)

        # analyze
        self.analyze = Label(name='automon/analyze', color=self._color_default)

        # enable auto reply
        self.auto_reply_enabled = Label(name='automon/auto reply enabled', color=self._color_default)

        # need user input
        self.user_action_required = Label(name='automon/user action required', color=self._color_error)

        # error
        self.error = Label(name='automon/error', color=self._color_error)

        # scheduled
        self.scheduled = Label(name='automon/scheduled', color=self._color_default)

        # waiting for interview
        self.waiting_for_interview = Label(name='automon/waiting for interview', color=self._color_default)

        # processing
        self.processing = Label(name='automon/processing', color=self._color_yellow)

        # skipped
        self.skipped = Label(name='automon/skipped', color=self._color_error)

    @property
    def all_labels(self):
        return [
            getattr(self, k) for k, v in vars(self).items()
            if type(v) == Label
            if 'automon' in v.name
        ]


class InternalDateSource:
    receivedTime = 'receivedTime'
    dateHeader = 'dateHeader'


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


class Color(DictHelper):
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

    backgroundColor: str
    textColor: str

    def __init__(self, color=None, backgroundColor: str = None, textColor: str = None):
        self.backgroundColor = str(backgroundColor).lower()
        self.textColor = str(textColor).lower()

        super().__init__(color)

    def __bool__(self):
        if self.backgroundColor and self.textColor:
            return True
        return False


class EmailAttachment(DictHelper):
    bytes: bytes
    filename: str
    mimeType: str
    content_type: str
    encoding: str

    def __init__(
            self,
            bytes_: bytes,
            filename: str = '',
            mimeType: str = None,
            content_type: str = None,
            encoding: str = None
    ):

        self._bytes = bytes_
        self.filename = filename
        self.mimeType = mimeType
        self._content_type = content_type
        self.encoding = encoding

        if mimeType:
            self.content_type, self.encoding = mimeType.split('/', 1)
        elif content_type and encoding:
            self.content_type = content_type
            self.encoding = encoding

        super().__init__()

    def __bool__(self):
        if self.bytes:
            return True
        return False

    @property
    def bytes(self):
        value = self._bytes
        self._bytes = bytes(value)
        return self._bytes

    @bytes.setter
    def bytes(self, value):
        self._bytes = bytes(value)

    @property
    def content_type(self):
        if self.mimeType:
            self.content_type, _ = self.mimeType.split('/', 1)
        return self._content_type

    @content_type.setter
    def content_type(self, value):
        self._content_type = value

    @property
    def encoding(self):
        if self.mimeType:
            _, self.encoding = self.mimeType.split('/', 1)
        return self._encoding

    @encoding.setter
    def encoding(self, value):
        self._encoding = value


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


class Header(DictHelper):

    def __init__(self, header: dict = None):

        self.name: str = ''
        self.value: str = ''

        super().__init__(header)

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


class HistoryType(DictHelper):
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


class Label(DictHelper):
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

    def __init__(
            self,
            label=None,
            id: str = None,
            name: str = None,
            color: Color = None,
            messageListVisibility: MessageListVisibility = MessageListVisibility.show,
            labelListVisibility: LabelListVisibility = LabelListVisibility.labelShow,
    ):
        self.id = id
        self.name = name
        self._color = color
        self.messageListVisibility = messageListVisibility
        self.labelListVisibility = labelListVisibility

        super().__init__(label)

    def __repr__(self):
        if self.name:
            return str(self.name)
        return str(self.id)

    def __eq__(self, other):
        if isinstance(other, Label):
            if self.id == other.id or self.name == other.name:
                return True
        return False

    def __lt__(self, other):
        if self.name < other.name:
            return True
        return False

    @property
    def color(self):
        value = self._color
        self._color = encapsulate(value, Color)
        return self._color

    @color.setter
    def color(self, value):
        self._color = encapsulate(value, Color)

    def _enhance(self):
        if hasattr(self, 'color'):
            self.color = Color().automon_update(self.color)


class LabelList(DictHelper):
    labels: list[Label]

    def __init__(self, labels: dict = None):
        self._labels = None

        super().__init__(labels)

    def __len__(self):
        return len(self.labels)

    @property
    def labels(self):
        value = self._labels
        self._labels = encapsulate(value=value, object_class=Label)
        return self._labels

    @labels.setter
    def labels(self, value):
        self._labels = encapsulate(value=value, object_class=Label)


class LabelAdded:
    pass


class LabelRemoved:
    pass


class MessagePartBody(DictHelper):
    """
    {
      "attachmentId": string,
      "size": integer,
      "data": string
    }
    """

    attachmentId: str
    size: int
    data: str

    def __init__(self, message: dict = None):

        self.attachmentId: str = None
        self.size: int = None
        self.data: str = None

        super().__init__(message)

    def __repr__(self):
        return repr_str([
            self._data_hash(),
            f'{round(self.size / 1024):,} KB',
        ])

    def __bool__(self):
        if self.size:
            if self.size > 0:
                return True
        if self.data:
            return True
        if self.attachmentId:
            return True
        return False

    def _data_base64decoded(self) -> bytes | None:
        if self.data:
            return base64.urlsafe_b64decode(self.data)

    def _data_BytesIO(self) -> io.BytesIO | None:
        if self.data:
            return io.BytesIO(self._data_base64decoded())

    def _data_html_text(self) -> str | None:
        if self.data:
            return self._html_text()

    def _data_decoded(self) -> str | None:
        if self.data:
            try:
                return self._data_base64decoded().decode()
            except:
                pass

    def _data_hash(self):
        if self.data:
            return hashlib.md5(self.data.encode()).hexdigest()

    def _data_bs4(self) -> bs4.BeautifulSoup | None:
        decoded = self._data_base64decoded()
        if decoded:
            return bs4.BeautifulSoup(decoded)

    def _html_text(self) -> str | None:
        if self._data_bs4():
            if self._data_bs4().html:
                return self._data_bs4().html.text


class MessagePart(DictHelper):
    partId: str
    mimeType: str
    filename: str
    headers: list[Header]
    body: MessagePartBody

    parts: list[Self]

    def __init__(self, part: dict = None):

        self.partId = None
        self.mimeType = None
        self.filename = None
        self._headers = []
        self._body = None

        self._parts = []

        super().__init__(part)

    def __repr__(self):
        return repr_str([
            self.filename,
            self.mimeType,
        ])

    @property
    def body(self):
        value = self._body
        self._body = encapsulate(value=value, object_class=MessagePartBody)
        return self._body

    @body.setter
    def body(self, value):
        self._body = encapsulate(value=value, object_class=MessagePartBody)

    @property
    def headers(self):
        value = self._headers
        self._headers = encapsulate(value=value, object_class=Header)
        return self._headers

    @headers.setter
    def headers(self, value):
        self._headers = encapsulate(value=value, object_class=Header)

    @property
    def parts(self):
        value = self._parts
        self._parts = encapsulate(value=value, object_class=MessagePart)
        return self._parts

    @parts.setter
    def parts(self, value):
        self._parts = encapsulate(value=value, object_class=MessagePart)

    def get_header(self, header: str) -> Header | None:
        for headers in self.headers:
            if header.lower() in headers.name.lower():
                return headers


class MessagePayload(DictHelper):
    partId: str
    mimeType: str
    filename: str
    headers: list[Header]
    body: MessagePartBody

    parts: list[MessagePart]
    size: int

    def __init__(self, message: dict = None):

        self._body = None
        self._headers = []
        self._parts = []
        self.size = None

        super().__init__(message)

    def __repr__(self):
        return repr_str([
            self.filename,
            self.mimeType,
            f"{self.size} B",
        ])

    def __bool__(self):
        if self.size is not None and self.size > 0:
            return True
        if self.parts:
            return True
        if self.body:
            return True
        return False

    @property
    def body(self):
        value = self._body
        self._body = encapsulate(value=value, object_class=MessagePartBody)
        return self._body

    @body.setter
    def body(self, value):
        self._body = encapsulate(value=value, object_class=MessagePartBody)

    @property
    def headers(self) -> list[Header]:
        value = self._headers
        self._headers = encapsulate(value=value, object_class=Header)
        return self._headers

    @headers.setter
    def headers(self, value):
        self._headers = encapsulate(value=value, object_class=Header)

    @property
    def parts(self):
        value = self._parts
        self._parts = encapsulate(value=value, object_class=MessagePart)
        return self._parts

    @parts.setter
    def parts(self, value):
        self._parts = encapsulate(value=value, object_class=MessagePart)

    def get_header(self, header: str) -> Header | None:
        for headers in self.headers:
            if header.lower() in headers.name.lower():
                return headers


class Message(DictHelper):
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
    """

    historyId: str
    id: str
    internalDate: str
    labelIds: list[Label]
    payload: MessagePayload
    raw: str
    sizeEstimate: str
    snippet: str
    threadId: str

    def __init__(self, message: dict = None):

        self.historyId = None
        self.id = None
        self.internalDate = None
        self._labelIds = []
        self._payload = None
        self.raw = None
        self.sizeEstimate = None
        self.snippet = None
        self.threadId = None

        super().__init__(message)

    def __repr__(self):
        labels = []
        labels_name = ['SENT', 'DRAFT', 'TRASH']
        for l in self.labelIds:
            if isinstance(l, Label):
                if l.name in labels_name:
                    labels.append(l)

        return repr_str([
            labels,
            self._date_since_now_str,
            self._email_from,
            self._header_subject,
            self.labelIds,
            self._date_utc_str,
        ])

    def __lt__(self, other):
        if isinstance(other, Message):
            if self._date_epoch_s < other._date_epoch_s:
                return True
        return False

    def __bool__(self):
        if self.id:
            return True
        return False

    def __eq__(self, other):
        if self.id == other.id:
            return True
        return False

    @property
    def labelIds(self):
        value = self._labelIds
        self._labelIds = sorted(encapsulate(value, Label))
        return self._labelIds

    @labelIds.setter
    def labelIds(self, value):
        self._labelIds = sorted(encapsulate(value, Label))

    @property
    def payload(self):
        value = self._payload
        self._payload = encapsulate(value, MessagePayload)
        return self._payload

    @payload.setter
    def payload(self, value):
        self._payload = encapsulate(value, MessagePayload)

    @property
    def _attachments(self) -> list[MessagePartBody | MessagePart]:
        payloads = []
        if self.payload:
            if self.payload.size:
                payloads.append(self.payload.body)
            if self.payload.parts:
                for parts in self.payload.parts:
                    payloads.append(parts)
        return payloads

    @property
    def _attachments_first(self) -> MessagePartBody | MessagePart | None:
        if self._attachments:
            return self._attachments[0]

    @property
    def _date_epoch_s(self) -> float | None:
        if self.internalDate:
            epoch_ms = int(self.internalDate)
            epoch_s = epoch_ms / 1000.0
            return epoch_s

    @property
    def _date_local(self):
        if self._date_epoch_s:
            date_local = datetime.datetime.fromtimestamp(self._date_epoch_s)
            return date_local

    @property
    def _date_local_str(self) -> str | None:
        if self._date_local:
            return str(self._date_local)

    @property
    def _date_utc(self):
        if self._date_epoch_s:
            date_utc = datetime.datetime.fromtimestamp(self._date_epoch_s, tz=datetime.timezone.utc)
            return date_utc

    @property
    def _date_utc_str(self) -> str | None:
        if self._date_utc:
            return str(self._date_local)

    @property
    def _date_since_now(self) -> datetime.timedelta | None:
        if self._date_local:
            automon_date = self._date_local
            time_delta = datetime.datetime.now()
            # time_delta = time_delta.replace(tzinfo=datetime.timezone(automon_date.utcoffset()))
            time_delta = time_delta - automon_date

            return time_delta

    @property
    def _date_since_now_str(self) -> str | None:
        if self._date_since_now:
            time_delta = self._date_since_now

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
    def _email_from(self) -> str | None:
        automon_header_from = self._header_from
        if automon_header_from:
            email = automon_header_from.value
            email = Regex().config_ignorecase().re_email().search(email).group()

            return email

    @property
    def _email_to(self) -> str | None:
        automon_header_to = self._header_to
        if automon_header_to:
            email = automon_header_to.value
            email = Regex().config_ignorecase().re_email().search(email).group()

            return email

    @property
    def _hash_md5(self) -> str:
        return hashlib.md5(self.id.encode()).hexdigest()

    @property
    def _header_from(self) -> Header | None:
        if self.payload:
            if self.payload.headers:
                return self.payload.get_header('From')

    @property
    def _header_subject(self) -> Header | None:
        if self.payload:
            if self.payload.headers:
                return self.payload.get_header('Subject')

    @property
    def _header_to(self) -> Header | None:
        if self.payload:
            if self.payload.headers:
                return self.payload.get_header('To')

    def _raw_decoded(self) -> str | None:
        if self.raw is not None:
            return base64.urlsafe_b64decode(self.raw).decode()

    def to_prompt(self) -> dict:
        email = {}
        email['from'] = self._email_from
        email['to'] = self._email_to
        email['subject'] = self._header_subject.value
        email['date'] = self._date_local_str
        email['date_epoch'] = self._date_epoch_s

        if self.payload:
            body = self.payload.body
            if body:
                text = body._data_html_text()
                if text:
                    email['body'] = text
            if self.payload.parts:
                parts = self.payload.parts
                for part in parts:
                    if part.mimeType == 'text/plain':
                        email['body'] = part.body._data_html_text()
                        break

                    more_parts = part.parts
                    for more_part in more_parts:
                        if more_part.mimeType == 'text/plain':
                            email['body'] = more_part.body._data_html_text()
                            break

        return email


class MessageAttachments(DictHelper):

    def __init__(self, attachments: list[dict] = []):

        self._attachments: list[dict] = None

        super().__init__(attachments)

    def __repr__(self):
        return f"{len(self.attachments)} attachments"

    def __bool__(self):
        if self.attachments:
            return True
        return False

    @property
    def attachments(self) -> list[MessagePart] | None:
        value = self._attachments
        self._attachments = encapsulate(value, MessagePart)
        return self._attachments

    @attachments.setter
    def attachments(self, value):
        self._attachments = encapsulate(value, MessagePart)

    @property
    def _first_attachment(self) -> MessagePart | None:
        for part in self.attachments:
            return part

    @property
    def _has_filename(self) -> list[MessagePart]:
        return [x for x in self.attachments if x.filename]


class MessageAdded:
    pass


class MessageDeleted:
    pass


class MessageList(DictHelper):
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

    messages: list[Message]
    resultSizeEstimate: str
    nextPageToken: str

    def __init__(self, messages: dict = None):

        self._messages = []
        self.resultSizeEstimate = None
        self.nextPageToken = None

        super().__init__(messages)

    def __repr__(self):
        if self.messages:
            return f'{len(self.messages)} messages'
        return ''

    def __bool__(self):
        if self.messages:
            return True
        return False

    @property
    def messages(self) -> list[Message]:
        self._messages = encapsulate(value=self._messages, object_class=Message)
        return self._messages

    @messages.setter
    def messages(self, value):
        self._messages = encapsulate(value=value, object_class=Message)


class Draft(DictHelper):
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

    def __init__(self, draft=None, id: str = None, message: Message = None):

        self.id: str = id
        self.message: Message = message

        super().__init__(draft)

    @property
    def automon_message(self) -> Message | None:
        if self.message:
            return Message(self.message)

    def __repr__(self):
        try:
            return f'{self.id} :: {self.message._header_subject.value}'
        except:
            return f"{self.id}"


class DraftList(DictHelper):
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

    def __init__(self, drafts: dict = None):
        self.drafts: list[Draft] = []
        self.nextPageToken: str = None
        self.resultSizeEstimate: int = None

        super().__init__(drafts)

    def __repr__(self):
        if self.drafts:
            return f"{len(self.drafts)} drafts"
        return str(self)


class Thread(DictHelper):
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

    id: str
    historyId: str
    messages: list[Message]
    snippet: str

    addLabelIds: list[str]
    removeLavelIds: list[str]

    def __init__(self, thread: dict = None):
        self.id: str = ''
        self.historyId: str = ''
        self._messages: list = []
        self.snippet: str = ''

        self.addLabelIds: list = []
        self.removeLabelIds: list = []

        super().__init__(thread)

    def __repr__(self):
        return repr_str([
            f'{self._messages_count} messages',
            self._message_first,
            self.id,
        ])

    def __lt__(self, other):
        if self._clean_thread_latest and other._clean_thread_latest:
            if self._clean_thread_latest._date_utc and other._clean_thread_latest._date_utc:
                if self._clean_thread_latest._date_utc < other._clean_thread_latest._date_utc:
                    return True
        return False

    def __bool__(self):
        if self.messages:
            return True
        return False

    @property
    def messages(self):
        value = self._messages
        self._messages = encapsulate(value, Message)
        return self._messages

    @messages.setter
    def messages(self, value):
        self._messages = encapsulate(value, Message)

    @property
    def _messages_count(self) -> int:
        return len(self.messages)

    @property
    def _clean_thread(self) -> list[Message]:
        """All messages excluding DRAFT"""
        messages = []
        labels = GmailLabels()

        for message in self.messages:
            if labels.draft not in message.labelIds:
                messages.append(message)

        return messages

    @property
    def _clean_thread_first(self) -> Message | None:
        if self._clean_thread:
            return self._clean_thread[0]

    @property
    def _clean_thread_latest(self) -> Message | None:
        if self._clean_thread:
            return self._clean_thread[-1]

    @property
    def _messages_count(self):
        return len(self.messages)

    @property
    def _messages_labels(self):
        labels = []
        for message in self.messages:
            for label in message.labelIds:
                if label not in labels:
                    labels.append(label)
        return sorted(labels)

    @property
    def _message_first(self) -> Message | None:
        if self.messages:
            return self.messages[0]

    @property
    def _message_latest(self) -> Message | None:
        if self.messages:
            return self.messages[-1]

    def to_prompt(self) -> list[dict]:
        return [{'message': x.to_prompt()} for x in self.messages]


class ThreadList(DictHelper):
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

    threads: list[Thread]
    nextPageToken: str
    resultSizeEstimate: int

    def __init__(self, threads: dict = None):
        self._threads = []
        self.nextPageToken = None
        self.resultSizeEstimate = None

        super().__init__(threads)

    def __repr__(self):
        return f"{len(self.threads)} threads"

    def __bool__(self) -> bool:
        if self.threads:
            return True
        return False

    @property
    def threads(self):
        self._threads = encapsulate(self._threads, Thread)
        return self._threads

    @threads.setter
    def threads(self, value):
        assert isinstance(value, list)
        self._threads = encapsulate(value, Thread)
