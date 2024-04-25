from app import app
from app.models import Users # The user table in the database
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import InputRequired, Length, ValidationError, Email

#need pip packages: email_validator, flask_wtf, flask_bcrypt, flask_login

# Custom validator - apply validator to email or username depending on login type
def username_or_email(form, field):
    if '@' in field.data:
        Email()(form, field)
    else:
        Length(min=4, max=20)(form, field)

class SignupForm(FlaskForm):
  username = StringField('Username', validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})
  email = StringField('Email', validators=[InputRequired(), Email(message='Invalid email address.')], render_kw={"placeholder": "Email"})
  password = PasswordField('Password', validators=[InputRequired(), Length(min=5, max=25)], render_kw={"placeholder": "Password"})
  submit = SubmitField("Register")

  def validate_username(self, username):
   existing_user = Users.query.filter_by(username=username.data).first()
   if existing_user:
      raise ValidationError("That username already exists. Please choose a different one.")

class LoginForm(FlaskForm):
    login = StringField('Username or Email', validators=[InputRequired(), username_or_email], render_kw={"placeholder": "Username or Email"})
    password = PasswordField('Password', validators=[InputRequired(), Length(min=5, max=25)], render_kw={"placeholder": "Password"})
    remember_me = BooleanField('Remember me')
    submit = SubmitField("Login")