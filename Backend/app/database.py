from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from app.exception_handling.database_exception import DatabaseExceptionError
import os
load_dotenv()

try:
    DATABASE = os.getenv("DATABASE_URL")
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

