
from flask_wtf import FlaskForm
from wtforms.fields import StringField
from wtforms.validators import InputRequired, Length, Regexp

class ActivationForm(FlaskForm):
    code = StringField(label='Verification code', validators=[
        InputRequired(),
        Length(min=6, max=6, message="Our verificaiton codes are 6 characters long."),
        Regexp(r"[0-9]{6}", flags=0, message="Our verificaiton codes only consist of digits."),
    ], render_kw = {
        "autocomplete": "one-time-code",
        "pattern": "[0-9]{6}",
        "inputmode": "numeric",
    })