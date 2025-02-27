import tempfile


class Tempfile(object):

    @classmethod
    def get_temp_dir(cls) -> str:
        return cls.gettempdir()

    @staticmethod
    def gettempdir():
        return tempfile.gettempdir()

    @classmethod
    def make_temp_dir(cls):
        return cls.mkdtemp()
        empdir()

    @classmethod
    def make_temp_file(cls):
        return cls.mkstemp()

    @staticmethod
    def mkdtemp():
        return tempfile.mkdtemp()

    @staticmethod
    def mkstemp():
        return tempfile.mkstemp()
