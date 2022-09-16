import minio


class Object(minio.datatypes.Object):
    bucket_name: str
    object_name: str

    def __init__(self, object: minio.datatypes.Object):
        self.__dict__.update(object.__dict__)

    def __repr__(self):
        return self.object_name


class DeleteObject(minio.deleteobjects.DeleteObject):
    name: str
    version_id: str

    def __init__(self, object: minio.deleteobjects.DeleteObject):
        self.__dict__.update(object.__dict__)
        self._name = object.object_name

    def __repr__(self):
        return self.name

    @property
    def bucket_name(self):
        return self._bucket_name

    @property
    def name(self):
        return self._name

    @property
    def version_id(self):
        return self._version_id
