from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import DateTime, ForeignKey, func
from datetime import datetime
from uuid import UUID
from app.db import Base

class AuthorizationCode(Base):
    __tablename__ = "authorization_codes"

    code: Mapped[str] = mapped_column(primary_key=True)
    application_id: Mapped[UUID] = mapped_column(ForeignKey("applications.id", ondelete="CASCADE"))
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    expires_at: Mapped[datetime] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)

    def __init__(self, code: str, client_uuid: UUID, user_uuid: UUID, exp: DateTime):
        self.code = code
        self.application_id = client_uuid
        self.user_id = user_uuid
        self.expires_at = exp