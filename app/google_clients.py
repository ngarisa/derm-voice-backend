# app/google_clients.py
import os
from dotenv import load_dotenv

from google.oauth2 import service_account
from googleapiclient.discovery import build

load_dotenv()

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/calendar"
]

def get_credentials():
    # Try environment variable first, then fallback to common file names
    cred_file = os.getenv("GOOGLE_CREDENTIALS_FILE")
    if not cred_file:
        # Check for common credential file names
        if os.path.exists("derm-voice-agent-04e08d6adce7.json"):
            cred_file = "derm-voice-agent-04e08d6adce7.json"
        elif os.path.exists("credentials.json"):
            cred_file = "credentials.json"
        else:
            raise FileNotFoundError(
                "Google credentials file not found. Set GOOGLE_CREDENTIALS_FILE environment variable "
                "or place credentials.json in the project root."
            )
    
    if not os.path.exists(cred_file):
        raise FileNotFoundError(f"Credentials file not found: {cred_file}")
    
    credentials = service_account.Credentials.from_service_account_file(
        cred_file, scopes=SCOPES
    )
    return credentials

def get_sheets_service():
    creds = get_credentials()
    service = build("sheets", "v4", credentials=creds)
    return service.spreadsheets()

def get_calendar_service():
    creds = get_credentials()
    service = build("calendar", "v3", credentials=creds)
    return service
