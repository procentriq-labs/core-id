from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import DateTime, ForeignKey, func

from passlib.context import CryptContext

from datetime import datetime
from uuid import UUID
from app.db import Base

class AuthorizationCode(Base):
    __tablename__ = "authorization_codes"
    _cyrpt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    code_identifier: Mapped[str] = mapped_column(primary_key=True)
    hashed_code: Mapped[str] = mapped_column(nullable=False)
    application_id: Mapped[UUID] = mapped_column(ForeignKey("applications.id", ondelete="CASCADE"))
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    scopes: Mapped[str] = mapped_column(nullable=False, server_default="")
    audience: Mapped[str] = mapped_column(nullable=False, server_default="")
    expires_at: Mapped[datetime] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)

    def __init__(self, code_identifier: str, code: str, client_uuid: UUID, user_uuid: UUID, exp: DateTime, scopes: str = "", audience: str = ""):
        self.application_id = client_uuid
        self.user_id = user_uuid
        self.expires_at = exp
        self.scopes = scopes
        self.audience = audience

        self.code_identifier = code_identifier
        self.hashed_code = self._cyrpt_context.hash(code)