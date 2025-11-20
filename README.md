# Dermatology Voice AI Agent Backend

A FastAPI backend service for a dermatology voice AI agent that integrates with Voiceflow. This service handles:

- **Call Logging**: Logs caller information (name, phone, email) to Google Sheets
- **Appointment Management**: Checks availability and books appointments via Google Calendar and Google Sheets
- **Voiceflow Integration**: RESTful API endpoints ready for Voiceflow webhook integration

## Features

- 📞 Log caller information to Google Sheets
- 📅 Check appointment slot availability
- 🗓️ Book appointments (updates Google Sheets and creates Google Calendar events)
- 📋 View appointments for a specific date
- 🏥 Health check endpoint for monitoring

## Setup

### Prerequisites

1. Python 3.10 or higher
2. Google Cloud Project with:
   - Google Sheets API enabled
   - Google Calendar API enabled
   - Service Account created with appropriate permissions

### Installation

1. Clone the repository and navigate to the project directory

2. Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up Google Service Account:
   - Create a service account in Google Cloud Console
   - Download the JSON credentials file
   - Place it in the project root as `derm-voice-agent-04e08d6adce7.json` (or update `.env`)

5. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your actual values
```

6. Set up Google Sheets:
   - Create a "Calls" sheet with headers: `Timestamp`, `Name`, `Phone`, `Email`, `Outcome`, `Intent`
   - Create an "Appointments" sheet with headers: `Date`, `Time`, `Provider`, `Status`, `Patient Name`, `Patient Email`, `Patient Phone`
   - Share both sheets with your service account email (found in the JSON credentials file)
   - Copy the Sheet IDs from the URLs and add them to `.env`

7. Set up Google Calendar:
   - Create a calendar (or use your primary calendar)
   - Share it with your service account email
   - Copy the Calendar ID and add it to `.env`

### Running the Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

API documentation: `http://localhost:8000/docs`

## API Endpoints

### POST `/api/call-log`
Log caller information to Google Sheets.

**Request Body:**
```json
{
  "name": "John Doe",
  "phone": "+1234567890",
  "email": "john@example.com",
  "outcome": "booked",
  "intent": "book"
}
```

**Response:**
```json
{
  "status": "ok"
}
```

### POST `/api/appointments/check`
Check if a time slot is available.

**Request Body:**
```json
{
  "date": "2024-01-15",
  "time": "14:30"
}
```

**Response:**
```json
{
  "available": true
}
```

### POST `/api/appointments/book`
Book an appointment slot.

**Request Body:**
```json
{
  "name": "John Doe",
  "phone": "+1234567890",
  "email": "john@example.com",
  "date": "2024-01-15",
  "time": "14:30"
}
```

**Response:**
```json
{
  "status": "booked"
}
```

**Error Response (409 Conflict):**
```json
{
  "detail": "Slot not available"
}
```

### GET `/api/appointments/today`
Get all appointments for today.

**Response:**
```json
{
  "date": "2024-01-15",
  "appointments": [
    {
      "date": "2024-01-15",
      "time": "14:30",
      "provider": "Dr. Smith",
      "status": "booked",
      "patientName": "John Doe",
      "patientEmail": "john@example.com",
      "patientPhone": "+1234567890"
    }
  ]
}
```

### GET `/health`
Health check endpoint.

**Response:**
```json
{
  "status": "healthy"
}
```

## Voiceflow Integration

To integrate with Voiceflow:

1. Deploy this backend to a cloud service (e.g., Heroku, Railway, AWS Lambda)
2. In Voiceflow, add a Webhook step with the following configuration:
   - **URL**: Your deployed backend URL (e.g., `https://your-backend.com/api/call-log`)
   - **Method**: POST
   - **Headers**: `Content-Type: application/json`
   - **Body**: Map Voiceflow variables to the API request format

### Example Voiceflow Webhook Configuration

For call logging:
```json
{
  "name": "{user_name}",
  "phone": "{user_phone}",
  "email": "{user_email}",
  "outcome": "{outcome}",
  "intent": "{intent}"
}
```

For checking availability:
```json
{
  "date": "{appointment_date}",
  "time": "{appointment_time}"
}
```

For booking:
```json
{
  "name": "{user_name}",
  "phone": "{user_phone}",
  "email": "{user_email}",
  "date": "{appointment_date}",
  "time": "{appointment_time}"
}
```

## Environment Variables

- `GOOGLE_CREDENTIALS_FILE`: Path to Google service account JSON file
- `CALLS_SHEET_ID`: Google Sheets ID for call logs
- `APPOINTMENTS_SHEET_ID`: Google Sheets ID for appointments
- `APPOINTMENTS_CALENDAR_ID`: Google Calendar ID for appointments
- `TIMEZONE`: IANA timezone (default: America/Chicago)

## Error Handling

All endpoints return appropriate HTTP status codes:
- `200`: Success
- `409`: Conflict (e.g., slot not available)
- `500`: Server error (check logs for details)

## Development

### Project Structure

```
derm-voice-backend/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI app and endpoints
│   ├── appointments.py  # Appointment and call logging logic
│   ├── google_clients.py # Google API client setup
│   └── config.py        # Configuration management
├── requirements.txt
├── .env.example
└── README.md
```

## License

MIT

# derm-voice-backend
