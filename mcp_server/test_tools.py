# test_tools.py
from tools import book_tool, cancel_tool, reschedule_tool
import pprint
pp = pprint.PrettyPrinter(indent=2)

print("Testing book tool...")
booking_payload = {
    "passenger_name": "Vaishak S",
    "origin": "BOM",
    "destination": "BLR",
    "date": "2025-10-10",
    "time": "10:30",
    "flight_class": "Economy"
}
book_res = book_tool(booking_payload)
pp.pprint(book_res)

booking_ref = book_res.get("booking_reference")
if booking_ref:
    print("\nTesting cancel tool...")
    cancel_res = cancel_tool(booking_ref)
    pp.pprint(cancel_res)

    print("\nTesting reschedule tool (rescheduling cancelled booking to test error handling)...")
    res_payload = {"booking_reference": booking_ref, "new_date": "2025-10-12", "new_time": "08:00"}
    res_res = reschedule_tool(res_payload)
    pp.pprint(res_res)
else:
    print("Booking failed; cannot run cancel/reschedule tests.")
