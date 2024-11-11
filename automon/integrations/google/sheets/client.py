from automon import log
from automon.integrations.google.auth import GoogleAuthClient

from .config import GoogleSheetsConfig

logger = log.logging.getLogger(__name__)
logger.setLevel(log.DEBUG)


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
            **kwargs
    ):
        super().__init__()
        self.config = config or GoogleSheetsConfig(
            spreadsheetId=spreadsheetId,
            **kwargs
        )

        self.worksheet = worksheet
        self.range = range

        self.response = None

    @property
    def values(self):
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
            **kwargs,
    ):
        """clear rows"""
        try:

            spreadsheets = self.spreadsheets()
            result = spreadsheets.values().clear(
                spreadsheetId=spreadsheetId or self.config.spreadsheetId,
                range=range or self.range,
                **kwargs,
            ).execute()

            logger.info(f'google :: sheets :: {result=}')
            logger.info(f"google :: sheets :: {result.get('clearedRange')} cells cleared.")
            return result
        except Exception as error:
            logger.error(f"google :: sheets :: {error=}")
            return error

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
            **kwargs,
    ):
        """get rows"""
        try:
            spreadsheets = self.spreadsheets()
            self.response = spreadsheets.get(
                spreadsheetId=spreadsheetId or self.config.spreadsheetId,
                ranges=ranges or self.range,
                includeGridData=includeGridData,
                fields=fields,
                **kwargs,
            ).execute()
            logger.info(f'google :: sheets :: {self.worksheet}!{self.range} ({self.config.spreadsheetId=})')
        except Exception as error:
            logger.error(f'google :: sheets :: {error=}')

        return self

    def get_values(
            self,
            spreadsheetId: str = None,
            range: str = None,
            **kwargs,
    ):
        """get values"""
        try:
            spreadsheets = self.spreadsheets()
            self.response = spreadsheets.values().get(
                spreadsheetId=spreadsheetId or self.config.spreadsheetId,
                range=range or f'{self.worksheet}!{self.range}',
                **kwargs,
            ).execute()

            logger.info(f'google :: sheets :: {self.worksheet=} :: {self.range=} :: {self.config.spreadsheetId=}')
        except Exception as error:
            logger.error(f'google :: sheets :: {error=}')

        return self

    def list(self):
        # list(pageSize=1).execute()
        logger.warning(f'{NotImplemented}')
        return

    def update(
            self,
            spreadsheetId: str = None,
            range: str = None,
            valueInputOption: ValueInputOption = ValueInputOption.USER_ENTERED,
            values: list = None,
    ):
        """update rows

        """
        try:

            body = {
                'values': values
            }

            logger.debug(f'google :: sheets :: {body=}')

            spreadsheets = self.spreadsheets()
            result = spreadsheets.values().update(
                spreadsheetId=spreadsheetId or self.config.spreadsheetId,
                range=range or self.range,
                valueInputOption=valueInputOption,
                body=body
            ).execute()

            logger.info(f'google :: sheets :: {result.get("updatedCells")} cells updated :: {result=}')
            return result
        except Exception as error:
            logger.error(f"google :: sheets :: {error=}")
            return error
