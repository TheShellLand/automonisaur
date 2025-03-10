import io
import bs4
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

    def delete(self, id: int): """requests.delete"""; return self.url + f'/drafts/{id}'

    def get(self, id: int): """requests.get"""; return self.url + f'/drafts/{id}'

    @property
    def list(self): """requests.get"""; return self.url + f'/drafts'

    @property
    def send(self): """requests.post"""; return self.url + f'/drafts/send'

    def update(self, id: int): """requests.put"""; return self.url + f'/drafts/{id}'


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

    def delete(self, id: int): """requests.delete"""; return self.url + f'/labels/{id}'

    def get(self, id: int): """requests.get"""; return self.url + f'/labels/{id}'

    def patch(self, id: int): """requests.get"""; return self.url + f'/labels/{id}'

    def update(self, id: int): """requests.get"""; return self.url + f'/labels/{id}'


class UsersMessages(Users):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def batchDelete(self): """post"""; return self.url + f'/messages/batchDelete'

    @property
    def batchModify(self): """post"""; return self.url + f'/messages/batchModify'

    def delete(self, id: int): """delete"""; return self.url + f'/messages/{id}'

    def get(self, id: str): """get"""; return self.url + f'/messages/{id}'

    @property
    def import_(self): """post"""; return self.url + f'/messages/import'

    @property
    def insert(self): """post"""; return self.url + f'/messages'

    @property
    def list(self): """get"""; return self.url + f'/messages'

    def modify(self, id: int): """post"""; return self.url + f'/messages/{id}/modify'

    @property
    def send(self): """post"""; return self.url + f'/messages/send'

    def trash(self, id: int): """post"""; return self.url + f'/messages/{id}/trash'

    def untrash(self, id: int): """post"""; return self.url + f'/messages/{id}/untrash'


class DictUpdate(dict):

    def __init__(self):
        super().__init__()

    def enhance(self):
        return self

    def __iter__(self):
        return self

    def update_dict(self, update: dict):
        if type(update) is not dict:

            if getattr(update, 'to_dict'):
                update = update.to_dict()
            else:
                raise Exception(f"I don't now what this is. {update=}")

        for key, value in update.items():
            setattr(self, key, value)

        self.enhance()
        return self

    def to_dict(self):
        return self.__dict__


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


class UsersThread:
    pass


class MessageListVisibility:
    show = 'show'
    hide = 'hide'


class LabelListVisibility:
    labelShow = 'labelShow'
    labelHide = 'labelHide'
    labelShowIfUnread = 'labelShowIfUnread'


class Type:
    system = 'system'
    user = 'user'


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


class Headers(DictUpdate):
    name: str
    value: str

    def __init__(self):
        super().__init__()
        self.enhance()

    def __repr__(self):
        if self.name:
            return f"{self.name}"


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

    def enhance(self):

        if hasattr(self, 'data'):
            setattr(self, 'automon_data_base64decoded', base64.urlsafe_b64decode(self.data))
            setattr(self, 'automon_data_BytesIO', io.BytesIO(self.automon_data_base64decoded))
            setattr(self, 'automon_data_bs4', bs4.BeautifulSoup(self.automon_data_base64decoded))

            try:
                setattr(self, 'automon_data_decoded', self.automon_data_base64decoded.decode())
            except Exception as error:
                setattr(self, 'automon_data_decoded', None)

            hash = self.automon_data_decoded

            setattr(self, 'automon_attachment', dict(decoded=self.automon_data_decoded,
                                                     base64decoded=self.automon_data_base64decoded,
                                                     BytesIO=self.automon_data_BytesIO,
                                                     bs4=self.automon_data_bs4,
                                                     hash_md5=cryptography.Hashlib.md5(hash)))

    def __repr__(self):
        if hasattr(self, 'attachmentId'):
            return f"{self.attachmentId}"


class MessagePart(DictUpdate):
    partId: str
    mimeType: str
    filename: str
    headers: [Headers]
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

    def enhance(self):

        if hasattr(self, 'body'):
            setattr(self, 'body', MessagePartBody().update_dict(self.body))

            if hasattr(self.body, 'automon_attachment'):
                setattr(self, 'automon_attachment', self.body.automon_attachment)

        if hasattr(self, 'headers'):
            setattr(self, 'headers', [Headers().update_dict(x) for x in self.headers])

        if hasattr(self, 'parts'):
            setattr(self, 'parts', [MessagePart().update_dict(x) for x in self.parts])

            setattr(self, 'automon_attachments', AutomonAttachments(attachments=self.parts))

        return self

    def __repr__(self):
        if getattr(self, 'filename') and getattr(self, 'mimeType'):
            return f"{self.filename} :: {self.mimeType}"
        elif getattr(self, 'mimeType'):
            return f"{self.mimeType}"


class AutomonAttachments(DictUpdate):
    attachments: [MessagePart]

    def __init__(self, attachments: MessagePart):
        super().__init__()

        self.attachments = attachments

    def from_hash(self, hash_md5: str):
        for attachment in self.attachments:
            if hash_md5 == attachment.automon_attachment['hash_md5']:
                return attachment
        raise Exception(f"[AutomonAttachments] :: from_hash :: hash not found {hash_md5} ::")


class Message(DictUpdate):
    id: str
    threadId: str
    labelIds: [str]
    snippet: str
    historyId: str
    internalDate: str
    payload: MessagePart
    sizeEstimate: str
    raw: str

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

    def enhance(self):

        if self.raw is not None:
            setattr(self, 'automon_raw_decoded', base64.urlsafe_b64decode(self.raw).decode())

        if hasattr(self, 'automon_raw_decoded'):
            setattr(self, 'automon_any_message', [self.automon_raw_decoded])

        if hasattr(self, 'payload'):
            setattr(self, 'payload', MessagePart().update_dict(self.payload))

            if hasattr(self.payload, 'headers'):

                for header in self.payload.headers:
                    if header.name == 'From':
                        setattr(self, 'automon_sender', header)
                    if header.name == 'Subject':
                        setattr(self, 'automon_subject', header)
                    if header.name == 'To':
                        setattr(self, 'automon_to', header)

            if hasattr(self.payload, 'automon_attachments'):
                setattr(self, 'automon_attachments', self.payload.automon_attachments)

        return self

    def __repr__(self):
        return f"{self.automon_labels} :: {self.automon_subject.value}"


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

    def __bool__(self):
        if hasattr(self, 'messages'):
            return True
        return False

    def enhance(self):
        if hasattr(self, 'messages'):
            setattr(self, 'messages', [Message().update_dict(message) for message in self.messages])

        return self

    def __repr__(self):
        return self.to_dict()


class MessageAdded:
    pass


class MessageDeleted:
    pass


class Draft(DictUpdate):
    id: str
    message: Message
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

        self.id = id
        self.message = message

    def enhance(self):
        if hasattr(self, 'message'):
            setattr(self, 'message', Message().update_dict(self.message))

    def to_dict(self):
        return dict(
            id=self.id,
            message=self.message.to_dict()
        )

    def __repr__(self):
        return f'{self.id} :: {self.message.automon_subject.value}'


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
        if color:
            self.color = color.to_dict()
        self.messageListVisibility = messageListVisibility
        self.labelListVisibility = labelListVisibility

    def __repr__(self):
        if self.name:
            return f"{self.name}"


class LabelAdded:
    pass


class LabelRemoved:
    pass


class HistoryType(DictUpdate):
    id: str
    messages: Message
    messagesAdded: MessageAdded
    messagesDeleted: MessageDeleted
    labelsAdded: LabelAdded
    labelsRemoved: LabelRemoved

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


class Format:
    minimal = 'minimal'
    full = 'full'
    raw = 'raw'
    metadata = 'metadata'


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
