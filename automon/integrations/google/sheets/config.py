from automon import log
from automon.helpers.osWrapper import environ
from automon.integrations.google.auth import GoogleAuthConfig

logger = log.logging.getLogger(__name__)
logger.setLevel(log.DEBUG)


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
