Examples (copy into mcp_server/examples/ if you like)

1) Booking (complete info)
User: "Book flight for Vaishak S from BOM to BLR on 2025-10-10 at 10:30"
Expected:
- intent: book
- slots: passenger_name=Vaishak S, origin=BOM, destination=BLR, date=2025-10-10, time=10:30
- assistant_text: Booking confirmed. Reference: BK-... BOM -> BLR on 2025-10-10 at 10:30.

2) Cancel (only booking ref)
User: "Please cancel my booking BK-20250928-abc12345"
Expected:
- intent: cancel
- slots: booking_reference=BK-20250928-abc12345
- assistant_text: Booking BK-20250928-abc12345 has been cancelled.

3) Reschedule (booking ref + new date/time)
User: "Reschedule BK-20250928-abc12345 to 2025-10-12 08:00"
Expected:
- intent: reschedule
- slots: booking_reference=..., date=2025-10-12, time=08:00
- assistant_text: Booking ... rescheduled to 2025-10-12 at 08:00.
