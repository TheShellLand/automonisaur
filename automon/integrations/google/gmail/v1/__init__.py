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


class InternalDateSource:
    receivedTime = 'receivedTime'
    dateHeader = 'dateHeader'


class UsersMessagesAttachments:
    pass


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


class Color:
    backgroundColor: str
    textColor: str

    """
    {
        'backgroundColor': '#ff7537', 
        'textColor': '#ffffff'
    }
    
    """
    pass


class DictUpdate:

    def update_dict(self, dict_: dict):
        self.__dict__.update(dict_)
        return self

    def to_dict(self):
        return self.__dict__


class Message(DictUpdate):
    id: str
    threadId: str
    labelIds: list
    snippet: str
    historyId: str
    internalDate: str
    payload: dict
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
            for part in self.automon_payload_parts:
                automon_data_decoded = part['body']['automon_data_decoded']
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
    def automon_payload_attachments(self):
        try:
            parts = self.payload['parts']

            message = []
            for part in parts:
                data = part['body']['data']
                message.append(
                    base64.urlsafe_b64decode(data)
                )
            return ''.join(message)
        except Exception as error:
            pass

    @property
    def automon_payload_body(self):
        try:
            return self.payload['body']
        except Exception as error:
            pass

    @property
    def automon_payload_body_decoded(self):
        try:
            data = self.automon_payload_body['data']
            data = base64.urlsafe_b64decode(data).decode()
            self.automon_payload_body['automon_data_decoded'] = data
            return data
        except Exception as error:
            pass

    @property
    def automon_payload_headers(self):
        try:
            return self.payload['headers']
        except:
            pass

    @property
    def automon_payload_mimeType(self):
        try:
            return self.payload['mimeType']
        except:
            pass

    @property
    def automon_payload_parts(self):
        try:
            for part in self.payload['parts']:
                body = part['body']
                if 'data' in body:
                    data = body['data']
                    body['automon_data_decoded'] = base64.urlsafe_b64decode(data).decode()

            return self.payload['parts']
        except:
            pass

    @property
    def automon_payload_sender(self):
        try:
            return [x for x in self.payload['headers'] if x['name'] == 'From'][0]
        except Exception as error:
            pass

    @property
    def automon_payload_subject(self):
        try:
            return [x for x in self.payload['headers'] if x['name'] == 'Subject'][0]
        except Exception as error:
            pass


    @property
    def automon_payload_to(self):
        try:
            return [x for x in self.payload['headers'] if x['name'] == 'To'][0]
        except Exception as error:
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


class MessageList(DictUpdate):
    messages: list
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

        self.automon_messages: Message = []

    def __bool__(self):
        if self.messages:
            return True
        return False

    def __repr__(self):
        return f"[MessageList] :: {len(self.messages)} messages ::"


class MessageAdded:
    pass


class MessageDeleted:
    pass


class MessagePartBody:
    """
    {
      "attachmentId": string,
      "size": integer,
      "data": string
    }
    """
    pass


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

    def __init__(self, name: str = None):
        self.name = name
        self.messageListVisibility = MessageListVisibility.show
        self.labelListVisibility = LabelListVisibility.labelShow


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
