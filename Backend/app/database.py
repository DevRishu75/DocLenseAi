from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from app.exception_handling.database_exception import DatabaseExceptionError
from pathlib import Path
import os

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

try:
    DATABASE = os.getenv("DATABASE_URL")
    if not DATABASE:
        raise RuntimeError("DATABASE_URL is not configured")
    if DATABASE.startswith("postgres://"):
        DATABASE = "postgresql://" + DATABASE[len("postgres://"):]
    engine = create_engine(DATABASE)
    SessionLocal = sessionmaker(
    autocommit = False,
    autoflush= False,
    bind= engine
)
except Exception as error:
    raise DatabaseExceptionError(
        message="Database failure happen",
        status_code=500,
        error_code="DATABASE_ERROR"
    )from error
