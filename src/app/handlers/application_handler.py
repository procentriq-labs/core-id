from app.db import get_db_session
from sqlalchemy.sql import exists

from uuid import UUID

from app.models.application.application_model import Application, ApplicationAuthFlow, ApplicationRedirectURI

from app.utils.uuid_utils import decode_short_uuid


class ApplicationHandler:
    @staticmethod
    def get_application_by_client_id(client_id: str) -> Application | None:
        application_uuid = decode_short_uuid(client_id)
        with get_db_session() as s:
            return s.query(Application).filter_by(id = application_uuid).one_or_none()

    @staticmethod
    def check_redirect_uri_allowed(application_id: UUID, redirect_uri: str) -> bool:
        with get_db_session() as session:
            return session.query(exists().where(ApplicationRedirectURI.application_id == application_id, ApplicationRedirectURI.redirect_uri == redirect_uri)).scalar()
        
    @staticmethod
    def check_authorization_flow_allowed(application_id: UUID, authorization_flow: str) -> bool:
        with get_db_session() as session:
            return session.query(exists().where(ApplicationAuthFlow.application_id == application_id, ApplicationAuthFlow.auth_flow == authorization_flow)).scalar()
        
    @staticmethod
    def check_secret(application: Application, secret: str) -> bool:
        with get_db_session() as session:
            application = session.merge(application)
            return application._cyrpt_context.verify(secret, application.hashed_client_secret)