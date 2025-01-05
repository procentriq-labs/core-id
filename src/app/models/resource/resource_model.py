from sqlalchemy import Column, String, Text, DateTime, UUID, func
from sqlalchemy.orm import relationship
from app.db import Base

class Resource(Base):
    __tablename__ = "resources"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4())
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    scopes = relationship("Scope", back_populates="resource")