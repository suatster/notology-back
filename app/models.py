import uuid
from datetime import datetime
from zoneinfo import ZoneInfo
from .database import Base
from app.core.config import settings
from sqlalchemy.dialects.postgresql import (
    UUID as SQL_UUID
)
from sqlalchemy.orm import relationship
from sqlalchemy import (
    Column, String, 
    Text, DateTime, 
    ForeignKey
)


class Users(Base):
    __tablename__ = 'users'

    id = Column(SQL_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(128), unique=True, index=True, nullable=False)
    email = Column(String(256), unique=True, index=True, nullable=False)
    hashed_password = Column(Text, nullable=False)
    created_at = Column(
        DateTime, 
        default=lambda: datetime.now(ZoneInfo(settings.TIMEZONE))
    )
    refresh_tokens = relationship(
        'RefreshToken', 
        back_populates='user', 
        cascade='all, delete-orphan'
    )

class RefreshToken(Base):
    __tablename__ = 'refresh_tokens'

    id = Column(SQL_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(SQL_UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'))
    token = Column(String(512), unique=True, index=True)
    expires_at = Column(DateTime(timezone=True))
    created_at = Column(
        DateTime, 
        default=lambda: datetime.now(ZoneInfo(settings.TIMEZONE))
    )
    user = relationship('Users', back_populates='refresh_tokens')
