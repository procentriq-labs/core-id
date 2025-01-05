from app.db import get_db_session
from sqlalchemy.sql import exists

from app.models.application.application_model import *


class ApplicationHandler:
    @staticmethod
    def check_redirect_uri_allowed(application_id: UUID, redirect_uri: str) -> bool:
        with get_db_session() as session:
            return session.query(exists().where(ApplicationRedirectURI.application_id == application_id, ApplicationRedirectURI.redirect_uri == redirect_uri)).scalar()
        
    @staticmethod
    def check_authorization_flow_allowed(application_id: UUID, authorization_flow: str) -> bool:
        with get_db_session() as session:
            return session.query(exists().where(ApplicationAuthFlow.application_id == application_id, ApplicationAuthFlow.auth_flow == authorization_flow)).scalar()