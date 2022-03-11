from .container import Container


class Response:
    count: int
    num_pages: int
    data: list

    def __init__(self, results: dict = None):
        self.data = None
        self.__dict__.update(results)

    def __repr__(self):
        return f'{self.__dict__}'
