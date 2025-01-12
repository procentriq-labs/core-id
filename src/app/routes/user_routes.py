from fastapi import APIRouter

import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/oauth2/userinfo")
async def get_userinfo():
    pass
    