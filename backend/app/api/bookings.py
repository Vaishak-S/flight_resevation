from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas, db
from datetime import datetime
import uuid

router = APIRouter()

# Dependency
get_db_session = db.get_db

# Helper function to generate booking reference
def generate_booking_reference():
    # Example: BK-20250928-UUID4
    return f"BK-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8]}"

# ----------------- BOOK -----------------
@router.post("/book-flight", response_model=schemas.BookingResponse)
def book_flight(booking: schemas.BookingCreate, db: Session = Depends(get_db_session)):
    booking_ref = generate_booking_reference()

    db_booking = models.Booking(
        passenger_name=booking.passenger_name,
        origin=booking.origin,
        destination=booking.destination,
        date=booking.date,
        time=booking.time,
        status="CONFIRMED",
        booking_reference=booking_ref
    )
    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)
    return db_booking

# ----------------- CANCEL -----------------
@router.post("/cancel-flight", response_model=schemas.BookingResponse)
def cancel_flight(cancel_req: schemas.CancelRequest, db: Session = Depends(get_db_session)):
    booking = db.query(models.Booking).filter_by(booking_reference=cancel_req.booking_reference).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    if booking.status == "CANCELLED":
        raise HTTPException(status_code=400, detail="Booking already cancelled")
    
    booking.status = "CANCELLED"
    db.commit()
    db.refresh(booking)
    return booking

# ----------------- RESCHEDULE -----------------
@router.post("/reschedule-flight", response_model=schemas.BookingResponse)
def reschedule_flight(reschedule_req: schemas.RescheduleRequest, db: Session = Depends(get_db_session)):
    booking = db.query(models.Booking).filter_by(booking_reference=reschedule_req.booking_reference).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    if booking.status == "CANCELLED":
        raise HTTPException(status_code=400, detail="Cannot reschedule a cancelled booking")
    
    booking.date = reschedule_req.new_date
    booking.time = reschedule_req.new_time
    booking.status = "RESCHEDULED"
    db.commit()
    db.refresh(booking)
    return booking
