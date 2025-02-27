import uuid


class Uuid:
    uuid: uuid = uuid

    @classmethod
    def hex(cls) -> str:
        return cls.uuid.uuid1().hex
