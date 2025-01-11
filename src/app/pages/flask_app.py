from flask import Flask
from jinjax import Catalog
from basic_components.utils.tailwind import tw
import os

flask_app = Flask(__name__, static_folder='assets/dist')

flask_app.config["SERVER_NAME"] = ""
flask_app.config["APPLICATION_ROOT"] = "/u/"
flask_app.config["SECRET_KEY"] = os.urandom(32)

flask_app.jinja_env.globals['cn'] = tw

catalog = Catalog(
    jinja_env=flask_app.jinja_env,
    root_url="/u/dist"
    )

catalog.add_folder("app/pages/components/ui")
catalog.add_folder("app/pages/components/layouts")
catalog.add_folder("app/pages/components/pages")