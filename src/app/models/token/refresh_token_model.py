from sqlalchemy import Column, String, Text, DateTime, ForeignKey, UUID, func
from app.db import Base
import uuid
from datetime import datetime, timezone, timedelta

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    token = Column(String, primary_key=True)
    application_id = Column(UUID(as_uuid=True), ForeignKey("applications.id", ondelete="CASCADE"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    scope = Column(Text, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    def __init__(self, token: str, application_uuid: uuid.UUID, user_uuid: uuid.UUID | None, scope_str: str, expires_in_s: int):
        self.token = token
        self.application_id = application_uuid
        self.user_id = user_uuid
        self.scope = scope_str
        self.expires_at = datetime.now(tz=timezone.utc) + timedelta(seconds=expires_in_s)
