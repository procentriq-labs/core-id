from app.models.organization.user_model import User

from app.db import get_db_session

class UserHandler:
    @staticmethod
    def get_user(email: str) -> User | None:
        with get_db_session() as s:
            return s.query(User).filter_by(email = email).one_or_none()

    @staticmethod
    def check_password(user: User, password: str) -> bool:
        return user._cyrpt_context.verify(password, user.hashed_password)