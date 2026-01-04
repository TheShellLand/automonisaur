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


class TableOptions(Enum):
    color: str
    icon: str


class TableType(Enum):
    """
    AI Text
    Attachment
    Auto number
    Barcode
    Button
    Checkbox
    Collaborator
    Count
    Created by
    Created time
    Currency
    Date
    Date and time
    Duration
    Email
    Formula
    Last modified by
    Last modified time
    Link to another record
    Long text
    Lookup
    Multiple collaborator
    Multiple select
    Number
    Percent
    Phone
    Rating
    Rich text
    Rollup
    Single line text
    Single select
    Sync source
    Url

    ref: https://airtable.com/developers/web/api/field-model
    """
    TYPE = ('singleLineText', 'checkbox')


class TableFieldType(Enum):
    TYPE = ('singleLineText', 'checkbox')


class TableField(Dict):
    description: str
    name: str
    type: str
    options: list[TableOptions]

    def __init__(
            self,
            name: str = 'field',
            description: str = '',
            type: TableType = 'singleLineText',
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


class AirtableApi:
    bases = BasesApi()
    tables = TablesApi()
    users = UsersApi()

    table_field = TableField
