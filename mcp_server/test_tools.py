from tools import book_tool, cancel_tool, reschedule_tool

# ----------------- Test Booking -----------------
booking_payload = {
    "passenger_name": "Vaishak S",
    "origin": "BOM",
    "destination": "BLR",
    "date": "2025-10-10",
    "time": "10:30",
    "flight_class": "Economy"
}

book_res = book_tool(booking_payload)
print("Book Response:", book_res)

# Extract booking_reference for further tests
booking_ref = book_res.get("booking_reference", "")

# ----------------- Test Cancel -----------------
if booking_ref:
    cancel_res = cancel_tool(booking_ref)
    print("Cancel Response:", cancel_res)

# ----------------- Test Reschedule -----------------
if booking_ref:
    reschedule_payload = {
        "booking_reference": booking_ref,
        "new_date": "2025-10-12",
        "new_time": "08:00"
    }
    reschedule_res = reschedule_tool(reschedule_payload)
    print("Reschedule Response:", reschedule_res)
