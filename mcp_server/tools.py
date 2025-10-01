import os
import requests
from typing import Dict
from datetime import datetime
import uuid

BASE_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000/flight-reservation")
TIMEOUT = 15
MOCK_BACKEND = os.getenv("MOCK_BACKEND", "true").lower() in ("1", "true", "yes")

def _mock_booking_response(payload: Dict) -> Dict:
    booking_reference = f"BK-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8]}"
    return {
        "booking_reference": booking_reference,
        "status": "CONFIRMED",
        "passenger_name": payload.get("passenger_name"),
        "origin": payload.get("origin"),
        "destination": payload.get("destination"),
        "date": payload.get("date"),
        "time": payload.get("time"),
    }

def book_tool(payload: Dict) -> Dict:
    if MOCK_BACKEND:
        return _mock_booking_response(payload)
    try:
        r = requests.post(f"{BASE_URL}/book-flight", json=payload, timeout=TIMEOUT)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"error": str(e)}

def cancel_tool(booking_reference: str) -> Dict:
    if MOCK_BACKEND:
        return {"booking_reference": booking_reference, "status": "CANCELLED"}
    try:
        payload = {"booking_reference": booking_reference}
        r = requests.post(f"{BASE_URL}/cancel-flight", json=payload, timeout=TIMEOUT)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"error": str(e)}

def reschedule_tool(payload: Dict) -> Dict:
    if MOCK_BACKEND:
        return {
            "booking_reference": payload.get("booking_reference"),
            "status": "RESCHEDULED",
            "date": payload.get("new_date"),
            "time": payload.get("new_time"),
        }
    try:
        r = requests.post(f"{BASE_URL}/reschedule-flight", json=payload, timeout=TIMEOUT)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"error": str(e)}
