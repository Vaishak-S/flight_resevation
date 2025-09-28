from fastapi import FastAPI
from .api import bookings
from .db import Base, engine

# Create DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Flight Booking API")

# Include router
app.include_router(bookings.router, prefix="/flight-reservation")
