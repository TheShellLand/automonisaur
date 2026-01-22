from automon.log.logger import Logging

log_LogStream = Logging('LogStream', Logging.ERROR)
logging_spaces = 0


class LogStream(object):
    def __init__(self):
        """Hold a bunch of logs
        """
        self.logs = []
        self.errors = []

    def store(self, log):
        """Logs are expected as a string list
        """
        output, error = log

        output = output.decode().splitlines()
        error = error.decode().splitlines()

        self.logs.extend(output)
        self.errors.extend(error)

        log_LogStream.debug(f'{len(self.logs)} lines')
        if self.errors:
            if len(self.errors) > 5:
                log_LogStream.error(f'{len(self.errors)} lines')
            else:
                log_LogStream.error(f'{self.errors}')

    def pop(self, index=0):
        """Pop a log off the top
        """
        try:
            log = self.logs.pop(index)
            log_LogStream.debug(log)
            return log
        except:
            return False
