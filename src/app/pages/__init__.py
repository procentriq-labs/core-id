from flask import Blueprint
from .login import login as login_router

user_pages = Blueprint('user_pages', __name__)

user_pages.register_blueprint(login_router)

__all__ = [
    "user_pages",
]