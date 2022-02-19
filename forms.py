from ast import Pass
from wsgiref.validate import validator
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField
from wtforms.validators import InputRequired, Length

class RegisterUserForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired(), Length(max=20)])
    password = PasswordField("Password", validators=[InputRequired()])
    email = EmailField("Email", validators=[InputRequired(), Length(max=50)])
    first_name = StringField("First Name", validators=[InputRequired(), Length(max=30)])
    last_name = StringField("Last Name", validators=[InputRequired(), Length(max=30)])

class UserLoginForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired(), Length(max=20)])
    password = PasswordField("Password", validators=[InputRequired()])

class FeedbackForm(FlaskForm):
    title = StringField("Title", validators=[InputRequired(), Length(max=100)])
    content = StringField("Content", validators=[InputRequired()])

class DeleteForm(FlaskForm):
    """fasdfas"""