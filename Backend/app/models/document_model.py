from sqlalchemy import Column,String,DateTime,ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from app.db.base import Base
import uuid

class Document(Base):
    __tablename__ = "documents"

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.user_id"),
        nullable=False
    )
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    filename = Column(
        String, nullable=False
    )
    created_at = Column(
        DateTime,
        default = datetime.utcnow,
        nullable = False
    )
    storage_key = Column(
        String,
        nullable=True
    )
     