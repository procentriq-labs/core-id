from app.pages.flask_app import flask_app

from requests.models import PreparedRequest
from urllib.parse import urljoin

def add_get_params(request, d: dict) -> str:
    url = urljoin(request.host_url, flask_app.url_for('verify.activate'))
    r = PreparedRequest()
    r.prepare_url(url, params={**request.args, **d})
    return r.url