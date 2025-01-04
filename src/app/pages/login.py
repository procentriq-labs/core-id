from flask import Blueprint

login = Blueprint('login', __name__)

@login.route('/login/id', methods=['GET', 'POST'])
def signup():
    return f"Hello from Flask!"