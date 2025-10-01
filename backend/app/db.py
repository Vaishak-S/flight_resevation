from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# PostgreSQL URL
# Replace the placeholders with your actual DB credentials
# Format: postgresql://username:password@host:port/database
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:@192.168.29.67:5432/flight_booking_db"

# Create engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=True  # optional: prints SQL queries for debugging
)

# Session local
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
