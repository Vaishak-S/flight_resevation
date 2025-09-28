from sqlalchemy import Column, Integer, String, Date, Time, DateTime
from sqlalchemy.sql import func
from .db import Base

class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    passenger_name = Column(String, nullable=False)
    origin = Column(String, nullable=False)        # 'from' is reserved keyword
    destination = Column(String, nullable=False)   # 'to' is reserved keyword
    date = Column(Date, nullable=False)
    time = Column(Time, nullable=False)
    status = Column(String, default="CONFIRMED")   # CONFIRMED, CANCELLED, RESCHEDULED
    booking_reference = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
