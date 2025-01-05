
from flask_wtf import FlaskForm
from wtforms import Form, FormField, StringField, PasswordField
from wtforms.validators import InputRequired, Email, EqualTo, Length

# Reused fields
_emailfield = StringField(label='Your E-mail', validators=[InputRequired(), Email()], render_kw={"type": "email", "placeholder": "account@your-mail.com"})

class LoginForm(FlaskForm):
    email = _emailfield
    password = PasswordField(label='Password', validators=[InputRequired(), Length(min=8, max=-1, message="Incorrect password. All passwords on our site are at least 8 characters long.")])

class ForgotPasswordEmailForm(FlaskForm):
    email = _emailfield

class SetPasswordForm(Form):
    password = PasswordField(label='Pick a strong Password', validators=[InputRequired(), Length(min=8, max=-1, message="Passwords must be at least 8 characters long")])
    password_confirm = PasswordField(label='Repeat Password', validators=[InputRequired(), EqualTo('password', message='Passwords must match')])

class SignupForm(FlaskForm):
    name = StringField(label='Your Name', validators=[InputRequired()], render_kw={"placeholder": "e.g., John Doe"})
    email = _emailfield
    pwd = FormField(SetPasswordForm)
    # accept_tos = BooleanField(label=Markup('I agree to the <a href="#">Terms of Service</a>.'), validators=[InputRequired(message="You need to agree to the Terms of Service.")])
    # accept_privacy = BooleanField(label=Markup('I agree to the <a href="#">Privacy Policy</a>.'), validators=[InputRequired(message="You need to agree to the Privacy Policy.")])