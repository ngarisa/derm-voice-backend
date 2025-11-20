# app/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import date

from .appointments import (
    log_call,
    check_slot_available,
    book_slot,
    get_appointments_for_date,
)

app = FastAPI(title="Derm Voice Backend")

# Add CORS middleware for Voiceflow integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify Voiceflow's domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------- Request models ---------

class CallLogRequest(BaseModel):
    name: str
    phone: str
    email: str
    outcome: str = "unknown"
    intent: str = "unknown"

class CheckSlotRequest(BaseModel):
    date: str  # "YYYY-MM-DD"
    time: str  # "HH:MM"

class BookSlotRequest(BaseModel):
    name: str
    phone: str
    email: str
    date: str
    time: str

# --------- Endpoints ---------

@app.post("/api/call-log")
def api_call_log(body: CallLogRequest):
    try:
        log_call(
            name=body.name,
            phone=body.phone,
            email=body.email,
            outcome=body.outcome,
            intent=body.intent,
        )
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to log call: {str(e)}")

@app.post("/api/appointments/check")
def api_check_slot(body: CheckSlotRequest):
    try:
        available = check_slot_available(body.date, body.time)
        return {"available": available}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to check slot: {str(e)}")

@app.post("/api/appointments/book")
def api_book_slot(body: BookSlotRequest):
    try:
        # check again inside book logic to avoid race
        success = book_slot(
            date_str=body.date,
            time_str=body.time,
            name=body.name,
            email=body.email,
            phone=body.phone,
        )
        if not success:
            raise HTTPException(status_code=409, detail="Slot not available")
        # optional: log call with outcome=booked
        log_call(body.name, body.phone, body.email, outcome="booked", intent="book")
        return {"status": "booked"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to book slot: {str(e)}")

@app.get("/api/appointments/today")
def api_appointments_today():
    try:
        today_str = date.today().isoformat()
        appts = get_appointments_for_date(today_str)
        return {"date": today_str, "appointments": appts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get appointments: {str(e)}")

@app.get("/health")
def health_check():
    """Health check endpoint for monitoring"""
    return {"status": "healthy"}
