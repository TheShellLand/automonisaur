from .container import Container


class ResultsContainer(object):
    count: int
    num_pages: int
    data: [Container]

    def __init__(self, results: dict = {}):
        self.data = None
        self.__dict__.update(results)

        if 'data' in results.keys():
            self.data = [Container(x) for x in self.data]

    def __repr__(self):
        return f'{self.__dict__}'
