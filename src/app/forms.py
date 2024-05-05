from app import app
from app.models import Users # The user table in the database
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import InputRequired, Length, ValidationError, Email
import re

# Custom validator - apply validator to email or username depending on login type
def username_or_email(form, field):
  if '@' in field.data:
    Email()(form, field)
  else:
    Length(min=4, max=20)(form, field)

# Ensure no spaces in the field
def noSpaces(form, field):
   if ' ' in field.data:
      raise ValidationError("The username must not contain spaces.")

# Password validation
def newPassword(form, field):
  if len(field.data) < 5 or len(field.data) > 25:
    raise ValidationError("Password must be between 5-25 characters long.")

  elif not re.match(r'^[a-zA-Z0-9!?+_\-]+$', field.data):
    raise ValidationError("Password can only include letters, numbers, and the following special characters: !, ?, -, +, _.")

  elif not re.search(r'[0-9]', field.data):
    raise ValidationError("Password must include at least one number.")

  elif not re.search(r'[A-Z]', field.data):
    raise ValidationError("Password must include at least one uppercase letter.")


class SignupForm(FlaskForm):
  username = StringField('Username', validators=[InputRequired(), noSpaces, Length(min=4, max=20)], render_kw={"placeholder": "Username"})
  email = StringField('Email', validators=[InputRequired(), Length(max=320), Email(message='Invalid email address.')], render_kw={"placeholder": "Email"})
  password = PasswordField('Password', validators=[InputRequired(), newPassword, Length(min=5, max=25)], render_kw={"placeholder": "Password"})
  submit = SubmitField("Register")

  def validate_username(self, username):
    existing_user = Users.query.filter_by(username=username.data).first()
    if existing_user:
      raise ValidationError("That username already exists. Please choose a different one.")

  def validate_email(self, email):
    existing_email = Users.query.filter_by(email=email.data).first()
    if existing_email:
      raise ValidationError("An account with this email already exists. Please use a different email.")

class LoginForm(FlaskForm):
  login = StringField('Username or Email', validators=[InputRequired(), username_or_email], render_kw={"placeholder": "Username/Email"})
  password = PasswordField('Password', validators=[InputRequired(), Length(min=5, max=25)], render_kw={"placeholder": "Password"})
  remember_me = BooleanField('Remember me')
  submit = SubmitField("Login")