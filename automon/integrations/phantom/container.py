class Container:
    def __init__(self, container: dict):
        self.__dict__.update(container)

    def __repr__(self):
        return f'' \
               f'name={self.name}, ' \
               f'status={self.status}, ' \
               f'id={self.id}, ' \
               f'artifacts={self.artifact_count}, ' \
               f'created={self.start_time} '
