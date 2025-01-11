from flask import Blueprint, flash, request, abort, url_for
from app.pages.flask_app import catalog

from app.pages.forms.auth_forms import LoginForm

from app.handlers.user_handler import UserHandler
from app.models.payloads.authorization_params import AuthorizeParams
from app.handlers.security_handler import SecurityHandler, InvalidResponseTypeException, InvalidRedirectURIException
from app.utils.uuid_utils import decode_short_uuid
from app.db import get_db_session
from app.config import load_settings

import logging

logger = logging.getLogger(__name__)

settings = load_settings()

login_router = Blueprint('login', __name__)

@login_router.route('/login', methods=['GET', 'POST'])
def login():
    try:
        params: AuthorizeParams = AuthorizeParams.model_validate(request.args.to_dict())
    except:
        abort(400)

    login_form = LoginForm(data=dict(
        email = request.args.get("email"),
    ))

    if login_form.validate_on_submit():
        with get_db_session() as session:
            u = UserHandler.get_user(login_form.email.data)
                    
            if u is not None:
                u = session.merge(u)
                
                if UserHandler.check_password(u, login_form.password.data):
                    try:
                        client_uuid = decode_short_uuid(params.client_id)
                        return SecurityHandler.respond_authorize(
                            client_uuid = client_uuid,
                            user_uuid = u.id,
                            response_types = params.response_type,
                            redirect_uri = params.redirect_uri,
                            state = params.state,
                        )
                    except ValueError:
                        logger.info(f"Failed to decode client_id {params.client_id}")
                    except InvalidRedirectURIException:
                        logger.info(f"Invalid redirect_uri {params.redirect_uri} for {params.client_id}")
                    except InvalidResponseTypeException as e:
                        logger.info(f"Received invalid request for disallowed response_type from {params.client_id}: {str(e)}")
                else:
                    logger.info(f"Error: Login failed for {login_form.email.data}: Invalid email or password.")
                    flash("Invalid e-mail or password", "error")
    
    return catalog.render(
        "LoginPage",
        form = login_form,
        signup_url = url_for('signup.signup', **params.model_dump()),
        tenant=settings.tenant_name,
    )