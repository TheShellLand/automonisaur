from minio.datatypes import Object as MinioObject


class Object(MinioObject):
    def __init__(self, object: MinioObject):
        self.__dict__.update(object.__dict__)

    def __repr__(self):
        return self.object_name
