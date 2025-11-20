# app/config.py
import os
from dotenv import load_dotenv

load_dotenv()

CALLS_SHEET_ID = os.getenv("CALLS_SHEET_ID")
APPOINTMENTS_SHEET_ID = os.getenv("APPOINTMENTS_SHEET_ID")
APPOINTMENTS_CALENDAR_ID = os.getenv("APPOINTMENTS_CALENDAR_ID")
TIMEZONE = os.getenv("TIMEZONE", "America/Chicago")
