from .flask_app import flask_app
from .routes.authentication.login_routes import login as login_router

flask_app.register_blueprint(login_router)

__all__ = [
    "flask_app",
]