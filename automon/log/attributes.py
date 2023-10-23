class LogRecordAttribute(object):

    def __init__(self, timestamp: bool = False):
        self._log_pattern = []

        if timestamp:
            self.asctime()

    def __repr__(self):
        return f'\t'.join(self._log_pattern)

    def __str__(self):
        return f'\t'.join(self._log_pattern)

    def ALL(self):
        self._log_pattern.append('[asctime]')
        self.asctime()
        self._log_pattern.append('[created]')
        self.created()
        self._log_pattern.append('[filename]')
        self.filename()
        self._log_pattern.append('[funcName]')
        self.funcName()
        self._log_pattern.append('[levelname]')
        self.levelname()
        self._log_pattern.append('[levelno]')
        self.levelno()
        self._log_pattern.append('[lineno]')
        self.lineno()
        self._log_pattern.append('[message]')
        self.message()
        self._log_pattern.append('[module]')
        self.module()
        self._log_pattern.append('[msecs]')
        self.msecs()
        self._log_pattern.append('[name]')
        self.name()
        self._log_pattern.append('[pathname]')
        self.pathname()
        self._log_pattern.append('[process]')
        self.process()
        self._log_pattern.append('[processName]')
        self.processName()
        self._log_pattern.append('[relativeCreated]')
        self.relativeCreated()
        self._log_pattern.append('[thread]')
        self.thread()
        self._log_pattern.append('[threadName]')
        self.threadName()
        # self._log_pattern.append('[taskName]')
        # self.taskName()

        return self

    def asctime(self):
        self._log_pattern.append('%(asctime)s')
        return self

    def created(self):
        self._log_pattern.append('%(created)f')
        return self

    def filename(self):
        self._log_pattern.append('%(filename)s')
        return self

    def funcName(self):
        self._log_pattern.append('%(funcName)s')
        return self

    def funcName_and_levelno(self):
        self._log_pattern.append('%(funcName)s:%(lineno)s')
        return self

    def levelname(self):
        self._log_pattern.append('%(levelname)s')
        return self

    def levelno(self):
        self._log_pattern.append('%(levelno)s')
        return self

    def lineno(self):
        self._log_pattern.append('%(lineno)d')
        return self

    def message(self):
        self._log_pattern.append('%(message)s')
        return self

    def module(self):
        self._log_pattern.append('%(module)s')
        return self

    def msecs(self):
        self._log_pattern.append('%(msecs)d')
        return self

    def name(self):
        self._log_pattern.append('%(name)s')
        return self

    def name_and_lineno(self):
        self._log_pattern.append('%(name)s:%(lineno)s')
        return self

    def pathname(self):
        self._log_pattern.append('%(pathname)s')
        return self

    def process(self):
        self._log_pattern.append('%(process)d')
        return self

    def processName(self):
        self._log_pattern.append('%(processName)s')
        return self

    def relativeCreated(self):
        self._log_pattern.append('%(relativeCreated)d')
        return self

    def thread(self):
        self._log_pattern.append('%(thread)d')
        return self

    def threadName(self):
        self._log_pattern.append('%(threadName)s')
        return self

    def taskName(self):
        self._log_pattern.append('%(taskName)s')
        return self
