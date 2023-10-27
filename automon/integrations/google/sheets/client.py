from automon.log import logger
from automon.integrations.google.auth import GoogleAuthClient

from .config import GoogleSheetsConfig

log = logger.logging.getLogger(__name__)
log.setLevel(logger.DEBUG)


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
            except Exception as e:
                pass

    def clear(
            self,
            range: str,
            spreadsheetId: str = None,
            **kwargs,
    ):
        """clear rows"""
        try:

            result = self.spreadsheets().values().clear(
                spreadsheetId=spreadsheetId or self.config.spreadsheetId,
                range=range or self.range,
                **kwargs,
            ).execute()

            log.info(f'{result}')
            log.info(f"{result.get('clearedRange')} cells cleared.")
            return result
        except Exception as error:
            log.error(f"An error occurred: {error}")
            return error

    def spreadsheets(self):
        """spreadsheet service"""
        return self.service().spreadsheets()

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
            self.response = self.spreadsheets().get(
                spreadsheetId=spreadsheetId or self.config.spreadsheetId,
                ranges=ranges or self.range,
                includeGridData=includeGridData,
                fields=fields,
                **kwargs,
            ).execute()
            log.info(f'{self.worksheet}!{self.range} ({self.config.spreadsheetId})')
        except Exception as e:
            log.error(f'{e}')

        return self

    def get_values(
            self,
            spreadsheetId: str = None,
            range: str = None,
            **kwargs,
    ):
        """get values"""
        try:
            self.response = self.spreadsheets().values().get(
                spreadsheetId=spreadsheetId or self.config.spreadsheetId,
                range=range or f'{self.worksheet}!{self.range}',
                **kwargs,
            ).execute()

            log.info(str(dict(
                worksheet=self.worksheet,
                range=self.range,
                spreadsheetId=self.config.spreadsheetId,
            )))
        except Exception as e:
            log.error(f'{e}')

        return self

    def list(self):
        # list(pageSize=1).execute()
        log.warning(f'{NotImplemented}')
        return

    def update(
            self,
            spreadsheetId: str = None,
            range: str = None,
            valueInputOption: ValueInputOption = ValueInputOption.USER_ENTERED,
            values: list = None,
    ):
        """update rows"""
        try:

            body = {
                'values': values
            }

            log.debug(f'{body}')

            result = self.spreadsheets().values().update(
                spreadsheetId=spreadsheetId or self.config.spreadsheetId,
                range=range or self.range,
                valueInputOption=valueInputOption,
                body=body
            ).execute()

            log.info(f'{result}')
            log.info(f"{result.get('updatedCells')} cells updated.")
            return result
        except Exception as error:
            log.error(f"An error occurred: {error}")
            return error
