from automon.helpers.loggingWrapper import LoggingClient, DEBUG, INFO
from automon.integrations.google.oauth import GoogleAuthClient

from .config import GoogleSheetsConfig

logger = LoggingClient.logging.getLogger(__name__)
logger.setLevel(DEBUG)


class Fields:
    hyperlink: str = 'sheets/data/rowData/values/hyperlink'


class ValueInputOption:
    USER_ENTERED: str = 'USER_ENTERED'
    RAW: str = 'RAW'


class GoogleSheetsClient(GoogleAuthClient):
    """Google Sheets client"""

    spreadsheetId: str
    worksheet: str
    range: str
    config: GoogleSheetsConfig

    def __init__(
            self,
            spreadsheetId: str = None,
            worksheet: str = '',
            range: str = 'A:Z',
            config: GoogleSheetsConfig = None,
            **kwargs):
        super().__init__()
        self.config = config or GoogleSheetsConfig(
            GOOGLE_SHEET_ID=spreadsheetId,
            **kwargs
        )

        self.spreadsheetId = self.config.GOOGLE_SHEET_ID

        self.worksheet = worksheet
        self.range = range

        self.response = None

    @property
    def sheet_values(self):
        """row values"""
        if self.response:
            try:
                return self.response['values']
            except Exception as error:
                pass

    def clear(
            self,
            range: str,
            spreadsheetId: str = None,
            **kwargs):
        """clear rows in spreadsheet"""

        spreadsheets = self.spreadsheets()
        result = spreadsheets.values().clear(
            spreadsheetId=spreadsheetId or self.config.GOOGLE_SHEET_ID,
            range=range or self.range,
            **kwargs,
        ).execute()

        logger.info(f'[GoogleSheetsClient] :: clear :: {result=}')
        logger.info(f"[GoogleSheetsClient] :: clear :: {result.get('clearedRange')} cells cleared.")
        return result

    def spreadsheets(self):
        """spreadsheet service"""
        service = self.service()
        return service.spreadsheets()

    def get(
            self,
            spreadsheetId: str = None,
            ranges: str = None,
            includeGridData: bool = False,
            fields: Fields or str = None,
            **kwargs):
        """get rows in spreadsheet"""

        spreadsheets = self.spreadsheets()
        self.response = spreadsheets.get(
            spreadsheetId=spreadsheetId or self.config.GOOGLE_SHEET_ID,
            ranges=ranges or self.range,
            includeGridData=includeGridData,
            fields=fields,
            **kwargs,
        ).execute()
        logger.info(
            f'[GoogleSheetsClient] :: '
            f'get :: '
            f'{self.worksheet}!{self.range} ({self.config.GOOGLE_SHEET_ID=})')

        return self

    def get_values(
            self,
            spreadsheetId: str = None,
            range: str = None,
            **kwargs, ):
        """get values from spreadsheet"""

        spreadsheets = self.spreadsheets()
        self.response = spreadsheets.values().get(
            spreadsheetId=spreadsheetId or self.config.GOOGLE_SHEET_ID,
            range=range or f'{self.worksheet}!{self.range}',
            **kwargs,
        ).execute()

        logger.info(
            f'[GoogleSheetsClient] :: '
            f'get values :: '
            f'{self.worksheet=} :: '
            f'{self.range=} :: '
            f'{self.config.GOOGLE_SHEET_ID=}')

        return self

    def list(self):
        # list(pageSize=1).execute()
        raise Exception(f'[GoogleSheetsClient] :: list :: {NotImplemented}')

    def update(
            self,
            spreadsheetId: str = None,
            range: str = None,
            valueInputOption: ValueInputOption = ValueInputOption.USER_ENTERED,
            values: list = None):
        """update rows in spreadsheet"""

        body = {
            'values': values
        }

        logger.debug(f'[GoogleSheetsClient] :: update :: {body=}')

        spreadsheets = self.spreadsheets()
        result = spreadsheets.values().update(
            spreadsheetId=spreadsheetId or self.config.GOOGLE_SHEET_ID,
            range=range or self.range,
            valueInputOption=valueInputOption,
            body=body
        ).execute()

        logger.info(
            f'[GoogleSheetsClient] :: '
            f'update :: '
            f'{result.get("updatedCells")} cells updated :: {result=}')
        return result
