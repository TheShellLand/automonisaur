from automon.log import Logging
from automon.integrations.google.auth import GoogleAuthClient

from .config import GoogleSheetsConfig

log = Logging(name='GoogleSheetsClient', level=Logging.DEBUG)


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

            print(f"{result.get('clearedRange')} cells cleared.")
            return result
        except Exception as error:
            print(f"An error occurred: {error}")
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
        except Exception as e:
            log.error(f'{e}', enable_traceback=False)

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
        except Exception as e:
            log.error(f'{e}', enable_traceback=False)

        return self

    def list(self):
        # list(pageSize=1).execute()
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

            result = self.spreadsheets().values().update(
                spreadsheetId=spreadsheetId or self.config.spreadsheetId,
                range=range or self.range,
                valueInputOption=valueInputOption,
                body=body
            ).execute()

            print(f"{result.get('updatedCells')} cells updated.")
            return result
        except Exception as error:
            print(f"An error occurred: {error}")
            return error
