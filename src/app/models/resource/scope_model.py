from sqlalchemy import Column, String, Text, UUID, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db import Base

class Scope(Base):
    __tablename__ = "scopes"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4())
    resource_id = Column(UUID(as_uuid=True), ForeignKey("resources.id", ondelete="CASCADE"))
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)

    resource = relationship("Resource", back_populates="scopes")

    __table_args__ = (UniqueConstraint("resource_id", "name", name="unique_scope_per_resource"),)