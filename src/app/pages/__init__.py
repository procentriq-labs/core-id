from .flask_app import flask_app
from .routes.authentication.login_routes import login_router
from .routes.authentication.signup_routes import signup_router

flask_app.register_blueprint(login_router)
flask_app.register_blueprint(signup_router)

__all__ = [
    "flask_app",
]