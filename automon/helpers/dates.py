from datetime import datetime, date


class Dates:
    @staticmethod
    def today():
        return datetime.today()

    @staticmethod
    def now():
        return datetime.now()

    @staticmethod
    def iso():
        return datetime.isoformat(datetime.now())

    @staticmethod
    def iso_short():
        return date.today().isoformat()

    @staticmethod
    def filename_timestamp():
        return f'{datetime.now().isoformat()}'.replace(':', '_')
