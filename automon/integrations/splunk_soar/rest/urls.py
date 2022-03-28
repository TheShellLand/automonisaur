from automon.log import Logging
from ..config import SplunkSoarConfig

config = SplunkSoarConfig()
log = Logging(name='Urls', level=Logging.DEBUG)


class Urls:
    """REST API endpoints

    /rest/<type>/[identifier]/[detail]?page=0&page_size=10&pretty&_filter_XXX='YYY'&_exclude_XXX='YYY'&include_expensive
    """
    HOST = config.host
    REST = f'{HOST}/rest'

    # type
    ACTION_RUN = f'{REST}/action_run'
    APP = f'{REST}/app'
    APP_RUN = f'{REST}/app_run'
    ARTIFACT = f'{REST}/artifact'
    ASSET = f'{REST}/asset'
    CLUSTER_NODE = f'{REST}/cluster_node'
    CONTAINER = f'{REST}/container'
    CONTAINER_ATTACHMENT = f'{REST}/container_attachment'
    PLAYBOOK = f'{REST}/playbook'
    PLAYBOOK_RUN = f'{REST}/playbook_run'
    VAULT = f'{REST}/vault_document'
    VAULT_ADD = f'{REST}/vault_add'
    VAULT_DELETE = f'{REST}/vault_delete'
    VAULT_INFO = f'{REST}/vault_info'

    GENERIC = f'{REST}/'

    @classmethod
    def generic(cls, api: str, identifier: int = None, detail: str = None, *args, **kwargs):
        return f'{cls.GENERIC}{api}{cls.query(identifier=identifier, detail=detail, *args, **kwargs)}'

    @classmethod
    def action_run(cls, identifier: int = None, detail: str = None, *args, **kwargs):
        return f'{cls.ACTION_RUN}{cls.query(identifier=identifier, detail=detail, *args, **kwargs)}'

    @classmethod
    def app(cls, identifier: int = None, detail: str = None, *args, **kwargs):
        return f'{cls.APP}{cls.query(identifier=identifier, detail=detail, *args, **kwargs)}'

    @classmethod
    def app_run(cls, identifier: int = None, detail: str = None, *args, **kwargs):
        return f'{cls.APP_RUN}{cls.query(identifier=identifier, detail=detail, *args, **kwargs)}'

    @classmethod
    def artifact(cls, identifier: int = None, detail: str = None, *args, **kwargs):
        return f'{cls.ARTIFACT}{cls.query(identifier=identifier, detail=detail, *args, **kwargs)}'

    @classmethod
    def asset(cls, identifier: int = None, detail: str = None, *args, **kwargs):
        return f'{cls.ASSET}{cls.query(identifier=identifier, detail=detail, *args, **kwargs)}'

    @classmethod
    def container(cls, identifier: int = None, detail: str = None, *args, **kwargs):
        return f'{cls.CONTAINER}{cls.query(identifier=identifier, detail=detail, *args, **kwargs)}'

    @classmethod
    def container_attachment(cls, identifier: int = None, detail: str = None, *args, **kwargs):
        return f'{cls.CONTAINER_ATTACHMENT}{cls.query(identifier=identifier, detail=detail, *args, **kwargs)}'

    @classmethod
    def cluster_node(cls, identifier: int = None, detail: str = None, *args, **kwargs):
        return f'{cls.CLUSTER_NODE}{cls.query(identifier=identifier, detail=detail, *args, **kwargs)}'

    @classmethod
    def exclude(cls, field_name: str, value: str or int or list or None):
        """Excluding

        docs: https://docs.splunk.com/Documentation/SOAR/current/PlatformAPI/RESTQueryData#Excluding

        Examples:
            /rest/endpoint?_exclude_<field_name>=<value>
            /rest/artifact?_exclude_tags__contains="preprocessed"
        """

        if isinstance(value, str):
            value = f'"{value}"'

        elif isinstance(value, int):
            value = int({value})

        elif isinstance(value, list):
            new_value = []

            for v in value:
                if isinstance(v, str):
                    new_value.append(f'"{v}"')
                elif isinstance(v, int):
                    new_value.append(f'{v}')
                else:
                    new_value.append(v)

            value = new_value

        return f'_exclude_{field_name}={value}'

    @classmethod
    def filter(cls, field_name: str, value: str or int or list or None):
        """Filtering

        docs: https://docs.splunk.com/Documentation/SOAR/current/PlatformAPI/RESTQueryData#Filtering

        Examples:
            /rest/endpoint?_filter_<field_name>=<value>

            &_filter_type="network"

        Type	Format	Example
        string	Enclosed in double or single quotes.	"myvalue"
        number	no formatting	10
        array	Python syntax for a literal list.	["a string", 2, None]
        """

        if isinstance(value, str):
            value = f'"{value}"'

        elif isinstance(value, int):
            value = int({value})

        elif isinstance(value, list):
            new_value = []

            for v in value:
                if isinstance(v, str):
                    new_value.append(f'"{v}"')
                elif isinstance(v, int):
                    new_value.append(f'{v}')
                else:
                    new_value.append(v)

            value = new_value

        return f'_filter_{field_name}={value}'

    @classmethod
    def playbook(cls, identifier: int = None, detail: str = None, *args, **kwargs):
        return f'{cls.PLAYBOOK}{cls.query(identifier=identifier, detail=detail, *args, **kwargs)}'

    @classmethod
    def playbook_run(cls, identifier: int = None, detail: str = None, *args, **kwargs):
        return f'{cls.PLAYBOOK_RUN}{cls.query(identifier=identifier, detail=detail, *args, **kwargs)}'

    @classmethod
    def params(cls, page: int = None,
               page_size: int = None,
               pretty: bool = None,
               filter: (str, str or int or list or None) = None,
               exclude: str = None,
               include_expensive: bool = None,
               sort: str = None,
               order: str = None, **kwargs) -> str:

        """General Form for a Parameters

        docs: https://docs.splunk.com/Documentation/SOAR/current/PlatformAPI/RESTQueryData#General_Form_for_a_Query

        ?page=0&page_size=10&pretty&_filter_XXX='YYY'&_exclude_XXX='YYY'&include_expensive

        Parameter	Required	Description
        type	required	The type of data being queried. Supported types are:
        action_run
        artifact
        asset
        app
        app_run
        container
        playbook_run
        cluster_node
        Querying for only a type will return a paginated array of objects.

        identifier	optional	Adding an identifier to a URL will retrieve a single specific object. Identifiers are integers and are unique for each resource.
        detail	optional	Adding a detail can only be done when querying a single object. The result is to return information on a single field of the object.
        page	optional	Positive integer. Returned results are paginated. This query parameter requests a specific page.
        page_size	optional	Positive integer. Returned results are paginated. This query parameter determines how many results returned per-page. Use "0" for all results.
        Setting page_size to 0 will return all results. Querying a very large data set can have an adverse effect on performance.

        pretty	optional	No value. Adding ?pretty (or &pretty) to your query will add related or calculated fields prefixed with _pretty_ to the response. For instance if the record you are looking for has a start_time, the response will have _pretty_start time that is a relative local version of the time. A record that has an "owner" reporting back an id will gain _pretty_owner that shows the owner's display name.
        Requesting pretty values is a relatively expensive call since it may involve expensive calculations or additional database lookups. When querying individual records or small numbers of records, this should not cause any performance hit. However if requesting tens of thousands of records it may have an adverse impact on your system depending on your hardware.

        _filter_XXX	optional	Add one or more filters to limit the results. Applies only to lists of objects. See Filtering below.
        _exclude_XXX	optional	Exclude matching items with syntax similar to filtering. See Excluding below.
        include_expensive	optional	No value. Adding this flag will cause the REST API to return all fields when returning a list, including large/expensive fields.
        The include_expensive parameter will return all fields, just as if you were requesting the individual record. These expensive fields may have megabytes of data for a single record, so use this option with caution as it may have a significant performance impact if returning large amounts of data.

        sort	optional	Field to sort results with. Can be any "simple" field at the top-level of record, such as a string, boolean, or integer value that is not under a hierarchy. Custom fields for events can also be sorted, using the format custom_fields.field_name.
        order	string	Either "asc" or "desc". This is the sorting order for the results.
        """

        params = []

        if page is not None:
            params.append(f'page={page}')

        if page_size is not None:
            params.append(f'page_size={page_size}')

        if pretty:
            params.append(f'pretty')

        if filter:
            field_name, value = filter
            params.append(f'{cls.filter(field_name=field_name, value=value)}')

        if exclude:
            params.append(f'{cls.exclude(exclude)}')

        if include_expensive:
            params.append(f'{include_expensive}')

        if sort:
            """field to sort by"""
            params.append(f'{sort}')

        if order:
            """asc or desc"""
            params.append(f'{order}')

        if params:
            params = f'?{"&".join(params)}'

        return params

    @classmethod
    def query(cls,
              identifier: int = None,
              detail: str = None,
              page: int = None,
              page_size: int = None,
              pretty: bool = None,
              filter: (str, str or int or list or None) = None,
              exclude: str = None,
              include_expensive: bool = None,
              sort: str = None,
              order: str = None, **kwargs):
        """General Form for a Query

        docs: https://docs.splunk.com/Documentation/SOAR/current/PlatformAPI/RESTQueryData#General_Form_for_a_Query

        ?page=0&page_size=10&pretty&_filter_XXX='YYY'&_exclude_XXX='YYY'&include_expensive

        Parameter	Required	Description
        type	required	The type of data being queried. Supported types are:
        action_run
        artifact
        asset
        app
        app_run
        container
        playbook_run
        cluster_node
        Querying for only a type will return a paginated array of objects.

        identifier	optional	Adding an identifier to a URL will retrieve a single specific object. Identifiers are integers and are unique for each resource.
        detail	optional	Adding a detail can only be done when querying a single object. The result is to return information on a single field of the object.
        page	optional	Positive integer. Returned results are paginated. This query parameter requests a specific page.
        page_size	optional	Positive integer. Returned results are paginated. This query parameter determines how many results returned per-page. Use "0" for all results.
        Setting page_size to 0 will return all results. Querying a very large data set can have an adverse effect on performance.

        pretty	optional	No value. Adding ?pretty (or &pretty) to your query will add related or calculated fields prefixed with _pretty_ to the response. For instance if the record you are looking for has a start_time, the response will have _pretty_start time that is a relative local version of the time. A record that has an "owner" reporting back an id will gain _pretty_owner that shows the owner's display name.
        Requesting pretty values is a relatively expensive call since it may involve expensive calculations or additional database lookups. When querying individual records or small numbers of records, this should not cause any performance hit. However if requesting tens of thousands of records it may have an adverse impact on your system depending on your hardware.

        _filter_XXX	optional	Add one or more filters to limit the results. Applies only to lists of objects. See Filtering below.
        _exclude_XXX	optional	Exclude matching items with syntax similar to filtering. See Excluding below.
        include_expensive	optional	No value. Adding this flag will cause the REST API to return all fields when returning a list, including large/expensive fields.
        The include_expensive parameter will return all fields, just as if you were requesting the individual record. These expensive fields may have megabytes of data for a single record, so use this option with caution as it may have a significant performance impact if returning large amounts of data.

        sort	optional	Field to sort results with. Can be any "simple" field at the top-level of record, such as a string, boolean, or integer value that is not under a hierarchy. Custom fields for events can also be sorted, using the format custom_fields.field_name.
        order	string	Either "asc" or "desc". This is the sorting order for the results.
        """
        query = ''
        params = cls.params(
            page=page,
            page_size=page_size,
            pretty=pretty,
            filter=filter,
            exclude=exclude,
            include_expensive=include_expensive,
            sort=sort,
            order=order, **kwargs
        )

        if identifier is not None:
            query += f'/{identifier}'

        if detail is not None:
            query += f'/{detail}'

        if params:
            query += f'{params}'

        return query

    @classmethod
    def vault(cls, identifier: int = None, *args, **kwargs):
        return f'{cls.VAULT}{cls.query(identifier=identifier, *args, **kwargs)}'

    @classmethod
    def vault_add(cls, identifier: int = None, *args, **kwargs):
        return f'{cls.VAULT_ADD}{cls.query(identifier=identifier, *args, **kwargs)}'

    @classmethod
    def vault_delete(cls, identifier: int = None, *args, **kwargs):
        return f'{cls.VAULT_DELETE}{cls.query(identifier=identifier, *args, **kwargs)}'

    @classmethod
    def vault_info(cls, identifier: int = None, *args, **kwargs):
        return f'{cls.VAULT_INFO}{cls.query(identifier=identifier, *args, **kwargs)}'
