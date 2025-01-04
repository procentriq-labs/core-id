from contextlib import contextmanager

from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

from app.config.loader import load_settings

settings = load_settings()
DATABASE_URL = str(settings.connections.database_url)

engine = create_engine(DATABASE_URL)

# Create a session factory
Sessionmaker = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for declarative models
Base = declarative_base()

# Dependency for getting the database session in FastAPI routes
@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    session = Sessionmaker()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()