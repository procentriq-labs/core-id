from flask import Blueprint, request, redirect, abort, url_for
from app.pages.flask_app import catalog

from app.pages.forms.auth_forms import SignupForm

from app.handlers.user_handler import UserHandler
from app.models.organization.user_model import User
from app.models.payloads.authorization_params import AuthorizeParams
from app.handlers.security_handler import SecurityHandler, InvalidResponseTypeException, InvalidRedirectURIException
from app.utils.uuid_utils import decode_short_uuid
from app.db import get_db_session
from app.config import load_settings

import logging

logger = logging.getLogger(__name__)

settings = load_settings()

signup_router = Blueprint('signup', __name__)

@signup_router.route('/signup', methods=['GET', 'POST'])
def signup():
    try:
        params: AuthorizeParams = AuthorizeParams.model_validate(request.args.to_dict())
        client_uuid = decode_short_uuid(params.client_id)
    except:
        abort(400)

    signup_form = SignupForm(data=dict(
        email = request.args.get("email"),
        name = request.args.get("name"),
    ))

    if signup_form.validate_on_submit():
        u = UserHandler.get_user(signup_form.email.data)
                
        if u is not None:
            # Email already exists.
            signup_form.email.errors.append("Email is already in use.")
        else:
            with get_db_session() as session:
                u = User(
                    name = signup_form.name.data,
                    email = signup_form.email.data,
                    password = signup_form.pwd.password.data,
                )
                session.add(u)
                session.commit()
            
                if(u.email_verified):
                    try:
                        return SecurityHandler.respond_authorize(
                            client_uuid = client_uuid,
                            user_uuid = u.id,
                            response_types = params.response_type,
                            redirect_uri = params.redirect_uri,
                            state = params.state,
                        )
                    except InvalidRedirectURIException:
                        logger.info(f"Invalid redirect_uri {params.redirect_uri} for {params.client_id}")
                    except InvalidResponseTypeException as e:
                        logger.info(f"Received invalid request for disallowed response_type from {params.client_id}: {str(e)}")
                else:
                    return redirect(url_for('verify.activate', subject=u.get_id(), **params.model_dump()))

    return catalog.render(
        "SignupPage",
        form = signup_form,
        login_url = url_for('login.login', **params.model_dump()),
        tenant=settings.tenant_name,
    )