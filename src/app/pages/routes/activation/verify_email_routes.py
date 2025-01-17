from flask import Blueprint, request, redirect, abort
from http import HTTPStatus
from app.pages.flask_app import catalog
from app.pages.forms.activation_forms import ActivationForm

from app.handlers.user_handler import UserHandler
from app.handlers.security_handler import SecurityHandler, InvalidResponseTypeException, InvalidRedirectURIException
from app.models.payloads.authorization_params import AuthorizeParams
from app.utils.uuid_utils import decode_short_uuid
from app.utils.format_utils import censor_email
from app.utils.url_utils import add_get_params
from app.db import get_db_session
from app.config import load_settings

from markupsafe import Markup

import logging

logger = logging.getLogger(__name__)
settings = load_settings()

verification_router = Blueprint('verify', __name__)

@verification_router.route('/activate', methods=['GET', 'POST'])
def activate():
    try:
        params: AuthorizeParams = AuthorizeParams.model_validate(request.args.to_dict())
        client_uuid = decode_short_uuid(params.client_id)
    except:
        logger.info("Aborting request due to malformed query parameters")
        abort(400)
    
    form = ActivationForm()

    mail_is_sent = request.args.get("mail_sent", 0, type=int) == 1

    try:
        user_id: str = request.args['subject']
        user_uuid = decode_short_uuid(user_id)
    except:
        logger.info("Aborting request due to malformed subject / user id")
        abort(HTTPStatus.BAD_REQUEST)

    with get_db_session() as s:
        user = s.merge(UserHandler.get_user_by_id(user_uuid))
        USER_EMAIL = user.email
        USER_NAME = user.name

    if not form.is_submitted() and not mail_is_sent:
        with get_db_session() as s:
            token = SecurityHandler.generate_verify_email_token(user_uuid)
            s.add(token)
            UserHandler.send_activation_email(USER_EMAIL, USER_NAME, token.token)
            mail_is_sent = True
        
    elif form.validate_on_submit():
        if(SecurityHandler.validate_user_otp(user_uuid, form.code.data)):
            UserHandler.activate_user(user_uuid)
            try:
                return SecurityHandler.respond_authorize(
                    client_uuid = client_uuid,
                    user_uuid = user_uuid,
                    response_types = params.response_type,
                    redirect_uri = params.redirect_uri,
                    state = params.state,
                    scopes_str=params.scope,
                    audience = params.audience,
                )
            except InvalidRedirectURIException:
                logger.info(f"Invalid redirect_uri {params.redirect_uri} for {params.client_id}")
            except InvalidResponseTypeException as e:
                logger.info(f"Received invalid request for disallowed response_type from {params.client_id}: {str(e)}")
        else:
            form.code.errors.append(Markup(f"Code is not valid. <a href='{add_get_params(request, dict(mail_sent = 0))}' class='underline text-zinc-950'>Request another</a>."))

    return catalog.render(
        "ActivateEmailPage",
        form = form,
        email = censor_email(USER_EMAIL),
        email_sent = mail_is_sent,
        tenant=settings.tenant_name,
    )
        