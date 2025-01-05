from flask import Blueprint
from app.pages.flask_app import catalog

from app.pages.forms.auth_forms import LoginForm

login = Blueprint('login', __name__)

@login.route('/login', methods=['GET', 'POST'])
def signup():
    login_form = LoginForm()

    if login_form.validate_on_submit():
        print("success")
    else:
        print("you're a failure!")

    return catalog.render(
        "LoginPage",
        form = login_form,
        # tenant="Test_Tenant",
    )