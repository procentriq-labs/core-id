from flask import Blueprint, flash, request, redirect
from app.pages.flask_app import catalog

from app.pages.forms.auth_forms import LoginForm

from app.handlers.user_handler import UserHandler
from app.models.payloads.authorization_params import AuthorizeParams
from app.handlers.security_handler import SecurityHandler, InvalidResponseTypeException, InvalidRedirectURIException
from app.utils.uuid_utils import decode_short_uuid
from app.db import get_db_session

from requests.models import PreparedRequest

import logging

logger = logging.getLogger(__name__)

login_router = Blueprint('login', __name__)

@login_router.route('/login', methods=['GET', 'POST'])
def login():
    params: AuthorizeParams = AuthorizeParams.model_validate(request.args.to_dict())

    login_form = LoginForm()

    if login_form.validate_on_submit():
        with get_db_session() as session:
            u = session.merge(UserHandler.get_user(login_form.email.data))
                    
            if u is not None and UserHandler.check_password(u, login_form.password.data):
                try:
                    client_uuid = decode_short_uuid(params.client_id)
                    SecurityHandler.authorize_validate_params(client_uuid, params)
                    authorization_code = SecurityHandler.generate_authorization_code(client_uuid, u.id)
                    session.add(authorization_code)
                    r = PreparedRequest()
                    # Assumes authorization_code flow, as no other flow with login_screen is supported :)
                    r.prepare_url(params.redirect_uri, params=dict(
                        authorization_code=authorization_code.code,
                        state=params.state,
                        )
                    )
                    return redirect(r.url, code=302)
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
        # tenant="Test_Tenant",
    )