from sqlalchemy import Column, String, Text, DateTime, ForeignKey, UUID, func
from app.db import Base

class AuthorizationCode(Base):
    __tablename__ = "authorization_codes"

    code = Column(String, primary_key=True)
    application_id = Column(UUID(as_uuid=True), ForeignKey("applications.id", ondelete="CASCADE"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    redirect_uri = Column(Text, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
