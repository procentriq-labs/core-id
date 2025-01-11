from .flask_app import flask_app
from .routes.authentication.login_routes import login_router
from .routes.authentication.signup_routes import signup_router
from .routes.activation.verify_email_routes import verification_router

flask_app.register_blueprint(login_router)
flask_app.register_blueprint(signup_router)
flask_app.register_blueprint(verification_router)

__all__ = [
    "flask_app",
]