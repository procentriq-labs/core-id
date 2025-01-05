from fastapi import APIRouter
from fastapi.responses import RedirectResponse

from app.pages import flask_app

import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/authorize")
async def authorize():
    return RedirectResponse(flask_app.url_for("login.signup", _external = False), 302)

