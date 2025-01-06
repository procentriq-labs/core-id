from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey, UUID, func
from sqlalchemy.orm import relationship
from app.db import Base

from passlib.context import CryptContext

from app.utils.uuid_utils import encode_short_uuid

class User(Base):
    __tablename__ = "users"
    _cyrpt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4())
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"))
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    email_verified = Column(Boolean, default=False, nullable=False)
    hashed_password = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    deleted_at = Column(DateTime, nullable=True)

    organization = relationship("Organization", back_populates="users")
    roles = relationship("Role", secondary="user_roles", back_populates="users")

    def __init__(self, name: str, email: str, password: str):
        self.name = name
        self.email = email

        self.hashed_password = self._cyrpt_context.hash(password)

    def get_id(self):
        return encode_short_uuid(self.id, User)

class Role(Base):
    __tablename__ = "roles"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4())
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)

    users = relationship("User", secondary="user_roles", back_populates="roles")

class UserRole(Base):
    __tablename__ = "user_roles"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True)

class RoleScopeMapping(Base):
    __tablename__ = "role_scope_mappings"

    role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True)
    scope_id = Column(UUID(as_uuid=True), ForeignKey("scopes.id", ondelete="CASCADE"), primary_key=True)
