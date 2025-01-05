import uvicorn
from fastapi import FastAPI
from flask import Flask
from fastapi.middleware.wsgi import WSGIMiddleware

from app.config import load_settings, configure_logging
from app.routes import api_router
from app.pages import flask_app

import logging

configure_logging()

logger = logging.getLogger(__name__)
settings = load_settings()

app = FastAPI(
    title = settings.app_name,
    version=settings.app_version,
    terms_of_service=str(settings.contact.tos_url),
    contact={
        "name": settings.contact.distributor_name,
        "url": str(settings.contact.distributor_website),
        "email": settings.contact.distributor_contact_email,
    },
    debug = settings.debug
)

app.include_router(api_router)

app.mount("/u/", WSGIMiddleware(flask_app))

if __name__ == "__main__":
    uvicorn.run(app, host=settings.app_host, port=settings.app_port, debug=settings.debug)
