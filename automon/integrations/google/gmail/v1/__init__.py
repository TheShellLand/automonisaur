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

    def __init__(self, *args):
        super().__init__(*args)

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


class UsersMessages:
    pass


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
    pass


class LabelListVisibility:
    pass


class Type:
    pass


class Color:
    pass


class Label:
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
    """

    def __init__(self):
        id: str = None
        name: str = None
        messageListVisibility: MessageListVisibility = None
        labelListVisibility: LabelListVisibility = None
        type: Type = None
        messagesTotal: int = None
        messagesUnread: int = None
        threadsTotal: int = None
        threadsUnread: int = None
        color: Color = None


class Message:
    pass


class Draft:
    """
    {
      "id": string,
      "message": {
        object (Message)
      }
    }
    """

    def __init__(self):
        id: str = None
        message: Message = None


class MessageAdded:
    pass


class MessageDeleted:
    pass


class LabelAdded:
    pass


class LabelRemoved:
    pass


class HistoryType:
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
        id: str = None
        messages: Message = None
        messagesAdded: MessageAdded = None
        messagesDeleted: MessageDeleted = None
        labelsAdded: LabelAdded = None
        labelsRemoved: LabelRemoved = None
