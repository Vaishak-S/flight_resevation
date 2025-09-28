import requests

BASE_URL = "http://127.0.0.1:8000/flight-reservation"  # FastAPI backend

# ----------------- BOOK TOOL -----------------
def book_tool(payload: dict) -> dict:
    """
    payload example:
    {
        "passenger_name": "Vaishak S",
        "origin": "BOM",
        "destination": "BLR",
        "date": "2025-10-10",
        "time": "10:30",
        "flight_class": "Economy"
    }
    """
    try:
        res = requests.post(f"{BASE_URL}/book", json=payload)
        res.raise_for_status()
        return res.json()
    except Exception as e:
        return {"error": str(e)}

# ----------------- CANCEL TOOL -----------------
def cancel_tool(booking_reference: str) -> dict:
    payload = {"booking_reference": booking_reference}
    try:
        res = requests.post(f"{BASE_URL}/cancel", json=payload)
        res.raise_for_status()
        return res.json()
    except Exception as e:
        return {"error": str(e)}

# ----------------- RESCHEDULE TOOL -----------------
def reschedule_tool(payload: dict) -> dict:
    """
    payload example:
    {
        "booking_reference": "BK-20250928-xxxx",
        "new_date": "2025-10-12",
        "new_time": "08:00"
    }
    """
    try:
        res = requests.post(f"{BASE_URL}/reschedule", json=payload)
        res.raise_for_status()
        return res.json()
    except Exception as e:
        return {"error": str(e)}
