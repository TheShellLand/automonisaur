## DEMISTO MOCK CLASSES FOR LOCAL DEBUGGING
try:
    from automon.integrations.xsoar.local_testing import *
    # from local_dev.common import *
except:
    pass


class SmaxEntity(Dict):

    def __init__(self, entity: dict | str = None):
        super().__init__()

        self.entities = []
        self.entity_type = ''
        self.properties = {}
        self.related_properties = {}

        if entity:
            self._update(entity)

    def __bool__(self):
        if self.automon_Id:
            return True
        return False

    def __repr__(self):
        if self.automon_Id and self.entity_type:
            return f'{self.entity_type} :: {self.automon_Id}'
        return f'{self.entity_type}'

    def __eq__(self, other):
        if self.automon_Id == other.automon_Id:
            return True
        return False

    @property
    def automon_Id(self):
        if self.properties:
            Id = self.properties['Id']
            debug(f'[SmaxEntity] :: update :: {Id=}', level=2)
            return Id
        return ''


class SmaxTicket(SmaxEntity):

    def __init__(self, ticket: dict = None):
        super().__init__()

        if ticket:
            self._update(ticket)

    @property
    def automon_ExpertAssignee(self) -> list | None:
        if self.related_properties:
            return [self._get_key_value(key='Name', value=self.related_properties.get('ExpertAssignee'))]

    @property
    def automon_ExpertGroup(self) -> list | None:
        if self.related_properties:
            return [self._get_key_value(key='Name', value=self.related_properties.get('ExpertGroup'))]

    @property
    def automon_RequestedByPerson(self) -> list | None:
        if self.related_properties:
            return [self._get_key_value(key='Name', value=self.related_properties.get('RequestedByPerson'))]

    @property
    def automon_RequestsOffering(self) -> list | None:
        if self.related_properties:
            return [self._get_key_value(key='DisplayLabel', value=self.related_properties.get('RequestsOffering'))]

    @property
    def automon_ManagerialContact_c(self) -> list | None:
        values = []
        for property in self.automon_complexTypeProperties:
            values.append(self._get_key_value(key='ManagerialContact_c', value=property.get('properties')))
        return [x for x in values if x]

    @property
    def automon_TechnicalContact_c(self) -> list | None:
        values = []
        for property in self.automon_complexTypeProperties:
            values.append(self._get_key_value(key='TechnicalContact_c', value=property.get('properties')))
        return [x for x in values if x]

    @property
    def automon_ArchitectName_c(self) -> list | None:
        values = []
        for property in self.automon_complexTypeProperties:
            values.append(self._get_key_value(key='ArchitectName_c', value=property.get('properties')))
        return [x for x in values if x]

    @property
    def automon_Comments(self) -> dict:
        import json
        return json.loads(self._get_key_value(key='Comments', value=self.properties))

    @property
    def automon_UserOptions(self) -> dict:
        import json
        return json.loads(self._get_key_value(key='UserOptions', value=self.properties))

    @property
    def automon_complexTypeProperties(self) -> list:
        value = self._get_key_value(key='complexTypeProperties', value=self.automon_UserOptions)
        if value:
            return value
        return []

    @property
    def automon_related_properties(self) -> dict:
        debug(f"[SmaxTicket] :: related_properties :: {self.related_properties}", level=4)
        return self.related_properties

    def _get_key_value(self, key: str, value: dict):
        key = key
        if value:
            value = value.get(key)
        debug(f"[SmaxTicket] :: _get_key_value :: {key} :: {value}", level=2)
        return value

    def update(self, ticket: dict):
        self._update(ticket)
        debug(f'[SmaxTicket] :: update :: {ticket=}', level=4)
        return self


class SmaxPerson(SmaxEntity):

    def __init__(self, person: dict | str = None):
        super().__init__()

        if person:
            self._update(person)

    def __repr__(self):
        return (f'{self.entity_type} :: '
                f'{self.automon_Id} :: '
                f'{self.automon_Email} :: '
                f'{self.automon_Name} :: '
                f'{self.automon_Title}')

    @property
    def automon_Email(self):
        debug(f"[SmaxPerson] :: Email :: {self.properties.get('Email')}")
        return self.properties.get('Email')

    @property
    def automon_Name(self):
        debug(f"[SmaxPerson] :: Name :: {self.properties.get('Name')}")
        return self.properties.get('Name')

    @property
    def automon_Title(self):
        debug(f"[SmaxPerson] :: Title :: {self.properties.get('Title')}")
        return self.properties.get('Title')

    def update(self, Person: dict):
        import json

        self._update(Person)
        debug(f"[SmaxPerson] :: update :: {self.to_json()}")
        return self


class SmaxQueryResponse(Dict):

    def __init__(self):
        super().__init__()

        self.Contents: dict = {}

    def __bool__(self):
        if self.Contents:
            return True
        return False

    def __eq__(self, other):
        if self.automon_hash == other.automon_hash:
            return True
        return False

    @property
    def automon_hash(self):
        import json
        import hashlib

        input_string = json.dumps(self.Contents).encode()
        return hashlib.md5(input_string).hexdigest()


class SmaxQueryTicketResponse(SmaxQueryResponse):

    def __init__(self, update: dict | str = None):
        super().__init__()

        if update:
            self._update(update)

    def __repr__(self):
        return f'{len(self.automon_smax_tickets())} smax tickets'

    def automon_smax_tickets(self) -> list[SmaxTicket]:
        Contents = self.Contents

        Tickets = []

        if Contents:
            assert type(Contents) == dict, f'{Contents=}'

            for entity in Contents.get('entities'):
                entity = SmaxTicket(entity)

                if entity not in Tickets:
                    Tickets.append(entity)

        debug(f'[SmaxQueryTicketResponse] :: automon_smax_tickets :: {Tickets=}', level=4)
        debug(f'[SmaxQueryTicketResponse] :: automon_smax_tickets :: {len(Tickets)} smax_entities', level=2)
        return Tickets


class SmaxQueryPersonResponse(SmaxQueryResponse):

    def __init__(self, update: dict | str = None):
        super().__init__()

        if update:
            self._update(update)

    def __repr__(self):
        return f'{len(self.automon_smax_entities())} smax persons'

    def automon_smax_entities(self) -> list[SmaxPerson]:
        Contents = self.Contents

        Persons = []

        if Contents:
            assert type(Contents) == dict, \
                f'[SmaxQueryPersonResponse] :: automon_smax_entities :: ERROR :: {Contents=}'

            for entity in Contents.get('entities'):
                entity = SmaxPerson(entity)

                if entity not in Persons:
                    Persons.append(entity)

        debug(f'[SmaxQueryPersonResponse] :: automon_smax_entities :: {Persons=}', level=4)
        debug(f'[SmaxQueryPersonResponse] :: automon_smax_entities :: {len(Persons)} smax_entities', level=2)
        return Persons
