# app/appointments.py
from datetime import datetime, timedelta
from typing import Optional, List, Dict
import pytz

from .google_clients import get_sheets_service, get_calendar_service
from .config import CALLS_SHEET_ID, APPOINTMENTS_SHEET_ID, APPOINTMENTS_CALENDAR_ID, TIMEZONE

sheets = get_sheets_service()
calendar = get_calendar_service()

# ----- Call logging -----

def log_call(name: str, phone: str, email: str,
             outcome: str = "unknown", intent: str = "unknown") -> None:
    """Log a call to Google Sheets"""
    if not CALLS_SHEET_ID:
        raise ValueError("CALLS_SHEET_ID not configured")
    
    timestamp = datetime.now().isoformat()
    values = [[timestamp, name, phone, email, outcome, intent]]
    body = {"values": values}
    sheets.values().append(
        spreadsheetId=CALLS_SHEET_ID,
        range="A:F",
        valueInputOption="RAW",
        body=body
    ).execute()

# ----- Appointments -----

def get_appointments_for_date(date_str: str) -> List[Dict]:
    """Get all appointments for a specific date"""
    if not APPOINTMENTS_SHEET_ID:
        raise ValueError("APPOINTMENTS_SHEET_ID not configured")
    
    result = sheets.values().get(
        spreadsheetId=APPOINTMENTS_SHEET_ID,
        range="A2:G"  # skip header
    ).execute()
    rows = result.get("values", [])
    appointments = []

    for row in rows:
        # row: [date, time, provider, status, patientName, patientEmail, patientPhone]
        if len(row) < 4:
            continue
        if row[0] == date_str:
            appointments.append({
                "date": row[0],
                "time": row[1],
                "provider": row[2],
                "status": row[3],
                "patientName": row[4] if len(row) > 4 else "",
                "patientEmail": row[5] if len(row) > 5 else "",
                "patientPhone": row[6] if len(row) > 6 else ""
            })
    return appointments

def check_slot_available(date_str: str, time_str: str) -> bool:
    """Check if a slot is available in the appointments sheet"""
    if not APPOINTMENTS_SHEET_ID:
        raise ValueError("APPOINTMENTS_SHEET_ID not configured")
    
    result = sheets.values().get(
        spreadsheetId=APPOINTMENTS_SHEET_ID,
        range="A2:D"  # date, time, provider, status
    ).execute()
    rows = result.get("values", [])

    for idx, row in enumerate(rows, start=2):  # start=2 because A2 is row 2
        if len(row) < 4:
            continue
        date, time, provider, status = row[0], row[1], row[2], row[3]
        if date == date_str and time == time_str and status.lower() == "available":
            return True
    return False

def book_slot(date_str: str, time_str: str,
              name: str, email: str, phone: str) -> bool:
    """
    Book a slot. Returns True if successfully booked, False if slot not available.
    """
    if not APPOINTMENTS_SHEET_ID:
        raise ValueError("APPOINTMENTS_SHEET_ID not configured")
    
    # Get all rows
    result = sheets.values().get(
        spreadsheetId=APPOINTMENTS_SHEET_ID,
        range="A2:G"
    ).execute()
    rows = result.get("values", [])

    # Find index of row to update
    row_to_update = None
    provider = None
    for idx, row in enumerate(rows, start=2):
        if len(row) < 4:
            continue
        date, time, prov, status = row[0], row[1], row[2], row[3]
        if date == date_str and time == time_str:
            if status.lower() != "available":
                return False
            row_to_update = idx
            provider = prov
            break

    if row_to_update is None:
        return False

    # Update the row: status → booked, fill patient info
    update_range = f"A{row_to_update}:G{row_to_update}"
    values = [[date_str, time_str, provider, "booked", name, email, phone]]
    body = {"values": values}

    sheets.values().update(
        spreadsheetId=APPOINTMENTS_SHEET_ID,
        range=update_range,
        valueInputOption="RAW",
        body=body
    ).execute()

    # Create calendar event
    create_calendar_event(date_str, time_str, name, email, phone)

    return True

def create_calendar_event(date_str: str, time_str: str,
                          name: str, email: str, phone: str):
    """Create a calendar event in Google Calendar"""
    if not APPOINTMENTS_CALENDAR_ID:
        raise ValueError("APPOINTMENTS_CALENDAR_ID not configured")
    
    # Parse date and time
    date_parts = date_str.split("-")
    time_parts = time_str.split(":")
    
    # Create timezone-aware datetime
    tz = pytz.timezone(TIMEZONE)
    start_dt = tz.localize(datetime(
        int(date_parts[0]),
        int(date_parts[1]),
        int(date_parts[2]),
        int(time_parts[0]),
        int(time_parts[1]),
        0
    ))
    
    # Add 30 minutes for appointment duration
    end_dt = start_dt + timedelta(minutes=30)

    event = {
        "summary": f"Dermatology Appointment - {name}",
        "description": f"Patient: {name}\nEmail: {email}\nPhone: {phone}",
        "start": {
            "dateTime": start_dt.isoformat(),
            "timeZone": TIMEZONE,
        },
        "end": {
            "dateTime": end_dt.isoformat(),
            "timeZone": TIMEZONE,
        },
    }

    calendar.events().insert(
        calendarId=APPOINTMENTS_CALENDAR_ID,
        body=event
    ).execute()
