from automon.log.logger import Logging


class SlackError:
    def __init__(self, error: Exception):
        """The request to the Slack API failed.
        The server responded with:
        {
            "ok": false,
            "error": "missing_scope",
            "needed": "users:read",
            "provided": "chat:write,chat:write.customize,chat:write.public,links:write,links:read,files:read,files:write"
        }
        """

        self._log = Logging(name=SlackError.__name__, level=Logging.ERROR)

        self._error = error
        self._reason = getattr(self._error, 'reason', '')
        self._response = getattr(self._error, 'response', '')

        if self._reason:
            self.args = getattr(self._reason, 'args', '')
            self.errno = getattr(self._reason, 'errno', '')
            self.reason = getattr(self._reason, 'reason', '')
            self.strerror = getattr(self._reason, 'strerror', '')
            self.verify_code = getattr(self._reason, 'verify_code', '')
            self.verify_message = getattr(self._reason, 'verify_message', '')

        if self._response:
            self.api_url = getattr(self._response, 'api_url' '')

            self.data = dict(getattr(self._response, 'data', ''))
            self.ok = self.data.get('ok', '')
            self.__error = self.data.get('error', '')
            self._needed = self.data.get('needed', '')
            self.provided = self.data.get('provided', '')

            self.headers = getattr(self._response, 'headers', '')
            self.http_verb = getattr(self._response, 'http_verb', '')
            self.req_args = getattr(self._response, 'req_args', '')
            self.status_code = getattr(self._response, 'status_code', '')

    def error(self):
        if self._response:
            return self.__error

        if self._reason:
            return self.strerror

        self._log.warn(f'{NotImplemented}')
        return f'{self._error}'

    def needed(self):
        if self._response:
            return self._needed

        if self._reason:
            return self.strerror

        self._log.warn(f'{NotImplemented}')
        return f'{self._error}'

    def __repr__(self):
        if self._response:
            return f'{self.data}'

        if self._reason:
            return f'{self.strerror}'

        self._log.warn(f'{NotImplemented}')
        return f'{self._error}'

    def __str__(self):
        return self.__repr__()
