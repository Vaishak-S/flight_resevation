# mcp_server/tools.py
import os
import requests
from typing import Dict

BASE_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000/flight-reservation")
TIMEOUT = 15

def book_tool(payload: Dict) -> Dict:
    try:
        r = requests.post(f"{BASE_URL}/book-flight", json=payload, timeout=TIMEOUT)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"error": str(e)}

def cancel_tool(booking_reference: str) -> Dict:
    try:
        payload = {"booking_reference": booking_reference}
        r = requests.post(f"{BASE_URL}/cancel-flight", json=payload, timeout=TIMEOUT)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"error": str(e)}

def reschedule_tool(payload: Dict) -> Dict:
    try:
        r = requests.post(f"{BASE_URL}/reschedule-flight", json=payload, timeout=TIMEOUT)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"error": str(e)}
