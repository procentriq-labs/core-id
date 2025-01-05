from flask import Blueprint
from app.pages.flask_app import catalog

from app.pages.forms.auth_forms import LoginForm

login = Blueprint('login', __name__)

@login.route('/login', methods=['GET', 'POST'])
def signup():
    login_form = LoginForm()
    return catalog.render(
        "LoginPage",
        form = login_form,
        # tenant="Test_Tenant",
    )