from automon.helpers.loggingWrapper import LoggingClient, DEBUG, INFO
from automon.helpers.osWrapper import environ
from automon.integrations.google.oauth import GoogleAuthConfig

logger = LoggingClient.logging.getLogger(__name__)
logger.setLevel(DEBUG)


class GoogleSheetsConfig(GoogleAuthConfig):
    """Google Sheets config"""

    def __init__(
            self,
            spreadsheetId: str = None,
    ):
        super().__init__()

        self.serviceName = 'sheets'
        self.scopes = [
            'https://www.googleapis.com/auth/drive',
            'https://www.googleapis.com/auth/drive.file',
            'https://www.googleapis.com/auth/drive.readonly',
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/spreadsheets.readonly',
        ]
        self.version = 'v4'

        self.spreadsheetId = spreadsheetId or environ('GOOGLE_SHEET_ID')

        logger.info(f'{self}')
