from sqlalchemy import Column, String, Boolean, ForeignKey, Text, DateTime, func, UUID
from sqlalchemy.orm import relationship

from passlib.context import CryptContext

from app.db import Base
from app.utils.uuid_utils import short_uuidable, encode_short_uuid

@short_uuidable
class Application(Base):
    __tablename__ = "applications"
    __idkey__ = "c"
    _cyrpt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4())
    name = Column(String, nullable=False)
    hashed_client_secret = Column(Text, nullable=False)  # Stored hashed client_secret
    is_first_party = Column(Boolean, nullable=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    auth_flows = relationship("ApplicationAuthFlow", back_populates="application")
    redirect_uris = relationship("ApplicationRedirectURI", back_populates="application")

    def __init__(self, name: str, secret: str, is_first_party: bool, created_by: UUID | None = None):
        self.name = name
        self.is_first_party = is_first_party
        self.created_by = created_by
        
        self.hashed_client_secret = self._cyrpt_context.hash(secret)

    def get_id(self):
        return encode_short_uuid(self.id, Application)

class ApplicationAuthFlow(Base):
    __tablename__ = "application_auth_flows"

    application_id = Column(UUID(as_uuid=True), ForeignKey("applications.id", ondelete="CASCADE"), primary_key=True)
    auth_flow = Column(String, primary_key=True)  # Example values: "authorization_code", "client_credentials"

    application = relationship("Application", back_populates="auth_flows")

class ApplicationRedirectURI(Base):
    __tablename__ = "application_redirect_uris"

    application_id = Column(UUID(as_uuid=True), ForeignKey("applications.id", ondelete="CASCADE"), primary_key=True)
    redirect_uri = Column(String, primary_key=True)

    application = relationship("Application", back_populates="redirect_uris")
