import io
import base64

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


class DictUpdate:

    def __iter__(self):
        return self

    def update_dict(self, dict_: dict):
        for key, value in dict_.items():
            setattr(self, key, value)
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
        self.backgroundColor = backgroundColor
        self.textColor = textColor


class Headers(DictUpdate):
    name: str
    value: str

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

    # def __init__(self):
    #     self.attachmentId = None
    #     self.data = None

    def __repr__(self):
        if hasattr(self, 'attachmentId'):
            return f"{self.attachmentId}"

    @property
    def automon_data_BytesIO(self):
        if hasattr(self, 'automon_data_decoded'):
            return io.BytesIO(self.automon_data_decoded)

    @property
    def automon_data_decoded(self):
        if hasattr(self, 'data'):
            return base64.urlsafe_b64decode(self.data)


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
        self._automon_parts = None
        self._automon_body = None

    @property
    def automon_body(self):
        if self._automon_body:
            return self._automon_body

        if self.body:
            return MessagePartBody().update_dict(self.body)

    @automon_body.setter
    def automon_body(self, update: MessagePartBody):
        self._automon_body = update

    @property
    def automon_headers(self):
        if self._automon_parts is not None:
            return self._automon_parts

        if self.headers:
            return [Headers().update_dict(x) for x in self.headers]
        return []

    @property
    def automon_parts(self):
        if hasattr(self, 'parts'):
            return [MessagePart().update_dict(x) for x in self.parts]
        return []

    @automon_parts.setter
    def automon_parts(self, parts: list):
        self._automon_parts = parts

    def __repr__(self):
        return f"{self.mimeType}"


class Message(DictUpdate):
    id: str
    threadId: str
    labelIds: list
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
        self.id = id
        self.threadId = threadId
        self.raw = raw

    @property
    def automon_any_message(self):
        try:
            if self.automon_raw_decoded:
                return [self.automon_raw_decoded]
        except Exception as error:
            pass

        try:
            parts = []
            for part in self.automon_payload.automon_parts:
                automon_data_decoded = part.body['automon_data_decoded']
                parts.append(automon_data_decoded)
            if parts:
                return parts
        except Exception as error:
            pass

    @property
    def automon_raw_decoded(self):
        try:
            raw = self.raw
            return base64.urlsafe_b64decode(raw).decode()
        except Exception as error:
            pass

    @property
    def automon_payload(self):
        try:
            return MessagePart().update_dict(self.payload)
        except:
            pass

    @property
    def automon_payload_headers_sender(self):
        try:
            return [x for x in self.automon_payload.automon_headers if x.name == 'From'][0]
        except Exception as error:
            pass

    @property
    def automon_payload_headers_subject(self):
        try:
            return [x for x in self.automon_payload.automon_headers if x.name == 'Subject'][0]
        except Exception as error:
            pass

    @property
    def automon_payload_headers_to(self):
        try:
            return [x for x in self.automon_payload.automon_headers if x.name == 'To'][0]
        except Exception as error:
            pass

    def __repr__(self):
        if self.id == self.threadId:
            return f"{self.id}"
        return f"{self.id} :: {self.threadId}"


class MessageList(DictUpdate):
    messages: Message
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
        self.messages = []

        self._automon_messages: Message = []

    @property
    def automon_messages(self):
        try:
            if self._automon_messages:
                return self._automon_messages
            return [Message().update_dict(message) for message in self.messages]
        except:
            pass

    @automon_messages.setter
    def automon_messages(self, messages: list):
        self._automon_messages = messages

    def __bool__(self):
        if self.messages:
            return True
        return False

    def __repr__(self):
        return f"{len(self.messages)} messages"


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
        self.id = id
        self.message = message


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
        self.drafts = None
        self.nextPageToken = None
        self.resultSizeEstimate = None

        self.automon_drafts = []


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

    def __init__(self, id: str = None, name: str = None, color: Color = None):
        self.id = id
        self.name = name
        if color:
            self.color = color.to_dict()
        self.messageListVisibility = MessageListVisibility.show
        self.labelListVisibility = LabelListVisibility.labelShow

        self.automon_labelIds = None

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
        pass


class Format:
    minimal = 'minimal'
    full = 'full'
    raw = 'raw'
    metadata = 'metadata'
