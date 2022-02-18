class Person:
    def __init__(self, contact: dict):
        """People Resource"""
        self.__dict__.update(contact)

    def __repr__(self):
        return f'{[x for x in self.get_names() for x in x.values() if isinstance(x, str)][-1]}'

    def to_dict(self):
        return dict(self.__dict__)

    def get_biographies(self):
        return self.__dict__.get('biographies', [])

    def get_memberships(self):
        return self.__dict__.get('memberships', [])

    def get_names(self):
        return self.__dict__.get('names', [])

    def get_phoneNumbers(self):
        return self.__dict__.get('phoneNumbers', [])
