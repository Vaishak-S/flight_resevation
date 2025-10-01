# backend/app/main.py
from fastapi import FastAPI
from .api import bookings
from .db import Base, engine

app = FastAPI(title="Flight Booking API")
app.include_router(bookings.router, prefix="/flight-reservation")

# create tables only when this module is run as the app (optional)
if __name__ != "__main__":
    # do not auto-create tables on import by other modules
    pass
# If you still want to support running this file directly with uvicorn:
if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
