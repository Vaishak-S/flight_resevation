from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .. import models, schemas, db

router = APIRouter()

# Dependency
get_db_session = db.get_db

@router.post("/book")
def book_flight(booking: schemas.BookingCreate, db: Session = Depends(get_db_session)):
    # Placeholder response
    return {"message": "Booking endpoint called", "data": booking.dict()}

@router.post("/cancel")
def cancel_flight(cancel_req: schemas.CancelRequest, db: Session = Depends(get_db_session)):
    # Placeholder response
    return {"message": "Cancel endpoint called", "data": cancel_req.dict()}

@router.post("/reschedule")
def reschedule_flight(reschedule_req: schemas.RescheduleRequest, db: Session = Depends(get_db_session)):
    # Placeholder response
    return {"message": "Reschedule endpoint called", "data": reschedule_req.dict()}
