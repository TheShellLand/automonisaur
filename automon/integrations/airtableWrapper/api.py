import json

from enum import Enum

from automon.helpers.dictWrapper import Dict


class V0(object):
    api: str = 'https://api.airtable.com/v0'


class UsersApi(V0):
    def info(self):
        """requests.get"""
        return f'{self.api}/meta/whoami'


class Base(Dict):
    id: str
    name: str
    permissionLevel: str

    def __bool__(self):
        if self.id and self.name and self.permissionLevel:
            return True
        return False


class BasesResponse(Dict):
    bases: list[Base]

    def __init__(self):
        super().__init__()
        self.bases = []

    def __bool__(self):
        if self.bases:
            return True
        return False

    def __len__(self):
        return len(self.bases)

    def __repr__(self):
        return f'{len(self.bases)} bases'

    def _enhance(self):
        self.bases = [Base().automon_update(x) for x in self.bases]

    def get_base(self, base_name: str) -> Base | None:
        for base in self.bases:
            if base.name == base_name:
                return base


class BasesApi(V0):
    def create(self):
        """requests.post"""
        return f'{self.api}/meta/bases'

    def list(self):
        """requests.get"""
        return f'{self.api}/meta/bases'

    def schema(self, baseId: str):
        """requests.get"""
        return f'{self.api}/meta/bases/{baseId}/tables'


class TableOptions(object):
    color: str
    icon: str
    number = {'precision': 3} # 0-8


class TableFieldType(object):
    """"""

    singleLineText = 'singleLineText'
    checkbox = 'checkbox'
    email = 'email'
    url = 'url'
    multilineText = 'multilineText'
    number = 'number'
    percent = 'percent'
    currency = 'currency'
    singleSelect = 'singleSelect'
    multipleSelects = 'multipleSelects'
    singleCollaborator = 'singleCollaborator'
    multipleCollaborators = 'multipleCollaborators'
    multipleRecordLinks = 'multipleRecordLinks'
    date = 'date'
    dateTime = 'dateTime'
    phoneNumber = 'phoneNumber'
    multipleAttachments = 'multipleAttachments'
    formula = 'formula'
    createdTime = 'createdTime'
    rollup = 'rollup'
    count = 'count'
    lookup = 'lookup'
    multipleLookupValues = 'multipleLookupValues'
    autoNumber = 'autoNumber'
    barcode = 'barcode'
    rating = 'rating'
    richText = 'richText'
    duration = 'duration'
    lastModifiedTime = 'lastModifiedTime'
    button = 'button'
    createdBy = 'createdBy'
    lastModifiedBy = 'lastModifiedBy'
    externalSyncSource = 'externalSyncSource'
    aiText = 'aiText'

    str = singleLineText
    int = number
    float = number


class TableField(Dict):
    description: str
    name: str
    type: str
    options: list[TableOptions]

    def __init__(
            self,
            name: str = 'field',
            description: str = '',
            type: TableFieldType = TableFieldType.singleLineText,
            options: list[TableOptions] = [],
    ):
        super().__init__()
        self.name = name
        self.description = description
        self.type = type
        if options:
            self.options = options

    def __bool__(self):
        if self.id and self.name and self.type:
            return True
        return False

    def __repr__(self):
        return f'{self.name} :: {self.type}'


class TableView(Dict):
    id: str
    name: str
    type: str

    def __bool__(self):
        if self.id and self.name:
            return True
        return False

    def __repr__(self):
        return f'{self.name} :: {self.type}'


class Table(Dict):
    description: str
    fields: list[TableField]
    id: str
    name: str
    primaryFieldId: str
    views: list[TableView]

    def __init__(self):
        super().__init__()

    def __bool__(self):
        if self.id and self.name:
            return True
        return False

    def __len__(self):
        return len(self.fields)

    def __repr__(self):
        if hasattr(self, 'name') and hasattr(self, 'fields'):
            return f'{self.name} :: {len(self.fields)} fields'
        return ''

    def _enhance(self):
        if hasattr(self, 'fields'):
            self.fields = [TableField().automon_update(x) for x in self.fields]
        if hasattr(self, 'views'):
            self.views = [TableView().automon_update(x) for x in self.views]


class TablesResponse(Dict):
    bases: list[Table]

    def __init__(self):
        super().__init__()
        self.tables = []

    def __bool__(self):
        if self.tables:
            return True
        return False

    def __len__(self):
        return len(self.tables)

    def __repr__(self):
        return f'{len(self)} tables'

    def _enhance(self):
        self.tables = [Table().automon_update(x) for x in self.tables]

    def table_get(self, name: str) -> Table | None:
        for table in self.tables:
            if table.name == name:
                return table
        return None


class TablesApi(V0):
    def create(self, baseId: str):
        """requests.post"""
        return f'{self.api}/meta/bases/{baseId}/tables'

    def list(self, baseId: str):
        """requests.get"""
        return f'{self.api}/meta/bases/{baseId}/tables'


class RecordField(Dict):

    def __init__(self, field: dict = None):
        super().__init__()

        if field:
            self.automon_update(field)

    def __len__(self):
        return self.__dict__.keys().__len__()

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


class Record(Dict):
    createdTime: str
    fields: dict[str, RecordField]
    id: str

    def __init__(self, fields: dict | RecordField = None):
        super().__init__()
        self.fields = fields

        if isinstance(fields, dict):
            self.fields = RecordField(fields)

    def __repr__(self):
        return f'{self.fields.__len__()} fields'

    def __eq__(self, other):
        if isinstance(other, Record):
            return self.fields == other.fields

    def _enhance(self):
        self.fields = RecordField().automon_update(self.fields)


class RecordsResponse(Dict):
    records: list[Record]

    def __init__(self):
        super().__init__()
        self.records = []

    def __repr__(self):
        return f'{self.records.__len__()} records'

    def __bool__(self):
        if self.records:
            return True
        return False

    def _enhance(self):
        self.records = [Record().automon_update(x) for x in self.records]


class RecordsApi(V0):

    def create(self, baseId: str, tableId: str = None, tableName: str = None):
        """requests.post"""
        if tableId:
            tableIdOrName = tableId

        if tableName:
            tableIdOrName = tableName

        return f'{self.api}/{baseId}/{tableIdOrName}'

    def delete(self, baseId: str, recordId: str, tableId: str = None, tableName: str = None):
        """requests.delete"""
        if tableId:
            tableIdOrName = tableId

        if tableName:
            tableIdOrName = tableName

        return f'{self.api}/{baseId}/{tableIdOrName}/{recordId}'

    def get(self, baseId: str, recordId: str, tableId: str = None, tableName: str = None):
        """requests.get"""
        if tableId:
            tableIdOrName = tableId

        if tableName:
            tableIdOrName = tableName

        return f'{self.api}/{baseId}/{tableIdOrName}/{recordId}'

    def list(self, baseId: str, tableId: str = None, tableName: str = None):
        """requests.get"""
        if tableId:
            tableIdOrName = tableId

        if tableName:
            tableIdOrName = tableName

        return f'{self.api}/{baseId}/{tableIdOrName}'

    def update(self, baseId: str, recordId: str, tableId: str = None, tableName: str = None):
        """requests.put requests.patch"""
        if tableId:
            tableIdOrName = tableId

        if tableName:
            tableIdOrName = tableName

        return f'{self.api}/{baseId}/{tableIdOrName}/{recordId}'


class AirtableApi:
    bases = BasesApi()
    tables = TablesApi()
    users = UsersApi()
    records = RecordsApi()

    TableField = TableField
    TableFieldType = TableFieldType
    TableOptions = TableOptions
    Record = Record
    RecordField = RecordField
