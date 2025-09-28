# API contract (quick reference — include in `docs/API_SPEC.md`)

* `POST /book`
  Request:

  ```json
  {
    "passenger_name": "Vaishak S",
    "from": "BOM",
    "to": "BLR",
    "date": "2025-10-10",
    "time": "10:30",
    "class": "Economy"
  }
  ```

  Response:

  ```json
  { "booking_reference": "BK-169...", "status": "CONFIRMED", "booking": { /* booking object */ } }
  ```
* `POST /cancel`

  ```json
  { "booking_reference": "BK-169..." }
  ```

  Response:

  ```json
  { "booking_reference": "BK-169...", "status": "CANCELLED" }
  ```
* `POST /reschedule`

  ```json
  { "booking_reference":"BK-169...", "new_date":"2025-10-12","new_time":"08:00" }
  ```

  Response:

  ```json
  { "booking_reference":"BK-169...", "status":"RESCHEDULED", "booking":{...} }
  ```
