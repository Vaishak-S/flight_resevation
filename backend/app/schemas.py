from pydantic import BaseModel
from datetime import date, time
from typing import Optional

# Booking creation
class BookingCreate(BaseModel):
    passenger_name: str
    origin: str
    destination: str
    date: date
    time: time
    flight_class: Optional[str] = "Economy"

# Booking response
class BookingResponse(BaseModel):
    booking_reference: str
    status: str
    passenger_name: str
    origin: str
    destination: str
    date: date
    time: time

    class Config:
        orm_mode = True

# Cancel request
class CancelRequest(BaseModel):
    booking_reference: str

# Reschedule request
class RescheduleRequest(BaseModel):
    booking_reference: str
    new_date: date
    new_time: time
