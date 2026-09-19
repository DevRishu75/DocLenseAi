from app.db.base import Base
from sqlalchemy import Column,String,DateTime,ForeignKey,Boolean
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.user_id"),
        nullable=False
    )
    token_hash = Column(
        String,nullable=False,unique=True
    )
    expires_at = Column(
        DateTime(timezone=True), nullable=False
    )
    revoked = Column(
        Boolean, nullable=False,default=False
    )
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow
    )