import json
import gspread
from google.oauth2.service_account import Credentials
from app.config import config

class GoogleSheetsService:
    """Handles Google Sheets operations for IT Asset Management."""

    SCOPES = [
        "https://www.googleapis.com/auth/spreadsheets.readonly",
        "https://www.googleapis.com/auth/drive"
    ]

    def __init__(self):
        """Initialize the Google Sheets client and connect to the specified sheet."""
        self.client = self.authenticate_google_sheets()
        self.sheet = self.connect_to_sheet(config.GOOGLE_SHEET_ID, config.GOOGLE_SHEET_NAME)

    def authenticate_google_sheets(self):
        """Authenticate with Google Sheets API using service account credentials."""
        credentials_dict = json.loads(config.GOOGLE_SHEETS_CREDENTIALS)  # Ensure credentials are loaded
        credentials = Credentials.from_service_account_info(credentials_dict, scopes=self.SCOPES)
        return gspread.authorize(credentials)

    def connect_to_sheet(self, spreadsheet_id, sheet_name):
        """
        Connect to a specific worksheet in a Google Sheets spreadsheet.

        Args:
            spreadsheet_id (str): ID of the spreadsheet.
            sheet_name (str): Name of the sheet (worksheet).

        Returns:
            gspread.models.Worksheet: The worksheet object.
        """
        spreadsheet = self.client.open_by_key(spreadsheet_id)
        sheet = spreadsheet.worksheet(sheet_name)
        return sheet

    def get_asset_details(self, service_tag):
        """Retrieve IT asset details from Google Sheets using Service Tag."""
        records = self.sheet.get_all_records()

        for record in records:
            if str(record.get("Service Tag")) == str(service_tag):  # Match using Service Tag
                return {
                    "Status": record.get("Status"),
                    "Previous User": record.get("Previous user"),
                    "Current User": record.get("Current user"),
                    "Hostname": record.get("Hostname"),
                    "Service Tag": record.get("Service Tag"),
                    "Laptop Model": record.get("Laptop model"),
                    "Location": record.get("Location")
                }
        return None
