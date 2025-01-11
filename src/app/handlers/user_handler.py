import resend

from app.pages.flask_app import catalog
from app.models.organization.user_model import User

from uuid import UUID

from app.db import get_db_session
from app.config import load_settings
from app.utils.format_utils import duration_in_words

settings = load_settings()

class UserHandler:
    @staticmethod
    def get_user(email: str) -> User | None:
        with get_db_session() as s:
            return s.query(User).filter_by(email = email).one_or_none()
        
    @staticmethod
    def get_user_by_id(user_uuid: UUID) -> User | None:
        with get_db_session() as s:
            return s.query(User).filter_by(id = user_uuid).one_or_none()

    @staticmethod
    def check_password(user: User, password: str) -> bool:
        return user._cyrpt_context.verify(password, user.hashed_password)
    
    @staticmethod
    def send_activation_email(user_email: str, user_name: str, otp: str) -> bool:
        APP_NAME = settings.tenant_name
        SENDER = f"{settings.email.sender_name} <{settings.email.sender_email}>"
        REPLY_TO = f"{settings.email.sender_name} <{settings.email.reply_email}>"
        RECIPIENT = f"{user_name} <{user_email}>"
        VALID_FOR_TEXT = duration_in_words(settings.security.email_verification_code_validity_seconds)
        
        resend.Emails.send({
            "from": SENDER,
            "reply_to": REPLY_TO,
            "to": RECIPIENT,
            "subject": f"Your code for {settings.tenant_name} is {otp}",
            "html": catalog.render(
                "EmailOTP",
                app_name = APP_NAME,
                recipient_name = user_name,
                recipient_email = user_email,
                otp = otp,
                otp_validity = VALID_FOR_TEXT,
            ),
        })
    
    @staticmethod
    def activate_user(user_uuid: UUID):
        with get_db_session() as s:
            u = s.merge(UserHandler.get_user_by_id(user_uuid))
            u.email_verified = True