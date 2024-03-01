
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError

from applications.models import Customer

class LoginForm(FlaskForm):
    username = StringField(label=('Enter username: '), validators = [InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(label=('Enter password: '), validators = [InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField("Login")

class UserRegisterForm(FlaskForm):
    username = StringField(label=('Choose username: '), validators = [InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(label=('Choose password: '), validators = [InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField("Register")

    def validate_username(self, username):
        existing_cust_name = Customer.query.filter_by(user_name = username.data).first()
        if existing_cust_name:
            raise ValidationError('This username already exists! Please choose a different one.')
        
    