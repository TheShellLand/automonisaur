import tempfile


class Tempfile(object):
    @staticmethod
    def gettempdir():
        return tempfile.gettempdir()

    @staticmethod
    def mkdtemp():
        return tempfile.mkdtemp()

    @staticmethod
    def mkstemp():
        return tempfile.mkstemp()
