from sqlalchemy import Column, String, DateTime, ForeignKey, UUID, func
from app.db import Base
from datetime import datetime

class VerifyEmailToken(Base):
    __tablename__ = "verify_email_tokens"

    token = Column(String, primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    def __init__(self, user_uuid: UUID, token: str, exp: datetime):
        self.user_id = user_uuid
        self.token = token
        self.expires_at = exp