from .container import Container


class GeneralResponse:
    def __init__(self, results: dict = {}):
        self.__dict__.update(results)

    def __repr__(self):
        return f'{self.__dict__}'


class Response(GeneralResponse):
    count: int
    num_pages: int
    data: list = None


class CreateContainerResponse(GeneralResponse):
    success: bool
    id: int = None
    new_artifacts_ids: list
