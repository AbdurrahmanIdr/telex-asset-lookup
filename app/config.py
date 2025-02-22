import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Configuration settings for Google Sheets integration."""

    # Google Sheets API
    GOOGLE_SHEETS_CREDENTIALS = os.getenv("GOOGLE_SHEETS_CREDENTIALS")
    GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID")
    GOOGLE_SHEET_NAME = os.getenv("GOOGLE_SHEET_NAME")

    # Telex Integration
    TELEX_WEBHOOK_SECRET = os.getenv("TELEX_WEBHOOK_SECRET")
    TELEX_TARGET_URL = os.getenv("TELEX_TARGET_URL")

config = Config()
