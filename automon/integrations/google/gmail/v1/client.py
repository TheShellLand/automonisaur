from automon.integrations.requests import RequestsClient

from .config import GmailConfig


class GmailClient:

    def __init__(self, api_key: str = None, user: str = None, password: str = None, config: GmailConfig = None):
        self.config = config or GmailConfig(user=user, password=password, api_key=api_key)
        self.endpoint = self.config.endpoint
        self.userId = self.config.userId

        self.client = RequestsClient()

    def _base_url(self, url: str):
        return f'{self.endpoint}{url}'

    def draft_create(self):
        """Creates a new draft with the DRAFT label."""
        api = [
            f'/gmail/v1/users/{self.userId}/drafts',
            f'/upload/gmail/v1/users/{self.userId}/drafts'
        ]
        return self.client.post(self._base_url(api[0]))

    def draft_delete(self, id: int):
        """Immediately and permanently deletes the specified draft."""
        api = f'/gmail/v1/users/{self.userId}/drafts/{id}'
        return self.client.delete(self._base_url(api))

    def draft_get(self, id: int):
        """Gets the specified draft."""
        api = f'/gmail/v1/users/{self.userId}/drafts/{id}'
        return self.client.get(self._base_url(api))

    def draft_list(self):
        """Lists the drafts in the user's mailbox."""
        api = f'/gmail/v1/users/{self.userId}/drafts'
        return self.client.get(self._base_url(api))

    def draft_send(self):
        """Sends the specified, existing draft to the recipients in the To, Cc, and Bcc headers."""
        api = [
            f'/gmail/v1/users/{self.userId}/drafts/send',
            f'/upload/gmail/v1/users/{self.userId}/drafts/send'
        ]
        return self.client.post(self._base_url(api[0]))

    def draft_update(self, id: int):
        api = [
            f'/gmail/v1/users/{self.userId}/drafts/{id}'
            f'/upload/gmail/v1/users/{self.userId}/drafts/{id}'
        ]
        return self.client.put(self._base_url(api[0]))

    def history_list(self):
        """Lists the history of all changes to the given mailbox."""
        api = f'/gmail/v1/users/{self.userId}/history'
        return self.client.get(self._base_url(api))

    def labels_create(self, label: str):
        """Creates a new label."""
        api = f'/gmail/v1/users/{self.userId}/labels'
        return self.client.post(self._base_url(api))

    def labels_delete(self, id: int):
        """Immediately and permanently deletes the specified label and
        removes it from any messages and threads that it is applied to."""
        api = f'/gmail/v1/users/{self.userId}/labels/{id}'
        return self.client.delete(self._base_url(api))

    def labels_get(self, id: int):
        """Gets the specified label."""
        api = f'/gmail/v1/users/{self.userId}/labels/{id}'
        return self.client.get(self._base_url(api))

    def labels_list(self):
        """Lists all labels in the user's mailbox."""
        api = f'/gmail/v1/users/{self.userId}/labels'
        return self.client.get(self._base_url(api))

    def labels_patch(self, id: int):
        """Patch the specified label."""
        api = f'/gmail/v1/users/{self.userId}/labels/{id}'
        return self.client.patch(self._base_url(api))

    def labels_update(self, id: int):
        """Updates the specified label."""
        api = f'/gmail/v1/users/{self.userId}/labels/{id}'
        return self.client.put(self._base_url(api))

    def users_watch(self):
        """Set up or update a push notification watch on the given user mailbox."""
        api = f'/gmail/v1/users/{self.userId}/watch'
        return self.client.post(self._base_url(api))

    def users_getProfile(self):
        """Gets the current user's Gmail profile."""
        api = f'/gmail/v1/users/{self.userId}/profile'
        return self.client.get(self._base_url(api))

    def users_stop(self):
        """Stop receiving push notifications for the given user mailbox."""
        api = f'/gmail/v1/users/{self.userId}/stop'
        return self.client.post(self._base_url(api))
