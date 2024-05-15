from app.models import Users # The user table in the database
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, IntegerField, EmailField
from wtforms.validators import InputRequired, Length, ValidationError, Email, NumberRange
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
def pass_characters(form, field):
    if not re.match(r'^[a-zA-Z0-9!?+_\-]+$', field.data):
        raise ValidationError("Password can only include letters, numbers, and the following special characters: !, ?, +, -, _.")

def pass_digit(form, field):
    if not re.search(r'[0-9]', field.data):
        raise ValidationError("Password must include at least one number.")

def pass_uppercase(form, field):
    if not re.search(r'[A-Z]', field.data):
        raise ValidationError("Password must include at least one uppercase letter.")


class SignupForm(FlaskForm):
    username = StringField(
        'Username',
        validators=[InputRequired(), Length(min=4, max=20), noSpaces],
        render_kw={"placeholder": "Username"})

    email = EmailField(
        'Email',
        validators=[InputRequired(), Email(message='Invalid email address.')],
        render_kw={"placeholder": "Email"})

    password = PasswordField(
        'Password', 
        validators=[InputRequired(), Length(min=5, max=25), pass_characters, pass_digit, pass_uppercase],
        render_kw={"placeholder": "Password"})
    
    submit = SubmitField("Register", id='signup-submit-button')

    def validate_username(self, username):
        existing_user = Users.query.filter_by(username=username.data).first()
        if existing_user:
            raise ValidationError("That username already exists. Please choose a different one.")

    def validate_email(self, email):
        existing_email = Users.query.filter_by(email=email.data).first()
        if existing_email:
            raise ValidationError("An account with this email already exists. Please use a different email.")


class LoginForm(FlaskForm):
    login = StringField(
        'Username or Email', 
        validators=[InputRequired(), username_or_email], 
        render_kw={"placeholder": "Username/Email"})

    password = PasswordField(
        'Password', 
        validators=[InputRequired(), Length(min=5, max=25)], 
        render_kw={"placeholder": "Password"})

    remember_me = BooleanField('Remember me')

    submit = SubmitField("Login", id='login-submit-button')


class PostForm(FlaskForm):
    post_name = StringField(
        'Name of ReQuest', 
        validators=[InputRequired(), Length(min=5, max=48)], 
        render_kw={"placeholder": "Track down gold atop Mount Dragon", "class": "form-control form-control-lg"},
        id="first-post-input")

    post_description = TextAreaField(
        'Description', 
        validators=[InputRequired(), Length(min=5, max=1000)], 
        render_kw={"placeholder": "I have left my gold atop Mount Dragon and need it back!", "class": "no-resize form-control form-control-lg", "rows": 10},
        id="second-post-input")
    
    post_reward = IntegerField(
        'Reward (Gold)',
        validators=[InputRequired(), NumberRange(min=0, message="Please enter a non-negative number.")],
        render_kw={"placeholder": "100", "class": "form-control form-control-lg"},
        id="third-post-input")
    
    submit = SubmitField("Submit", 
        render_kw={"class": "btn btn-lg btn-success rounded disabled"},
        id="submit-post")

    
class SearchForm(FlaskForm):
    post_search_name = StringField(
        'Search for ReQuest', 
        validators=[Length(max=48)], 
        render_kw={"placeholder": "Track down gold atop Mount Dragon", "class": "form-control form-control-lg"},
        id="search-input")

    submit = SubmitField(
        "Submit", 
        render_kw={"class": "btn btn-success rounded disabled"},
        id="submit-search")

    show_all = SubmitField(
        "Show All", 
        render_kw={"class": "btn btn-primary rounded"},
        id="show-all-search")
    

class ResponseForm(FlaskForm):
    response = TextAreaField(
        'Response', 
        validators=[InputRequired(), Length(max=1000)], 
        render_kw={"placeholder": "I have found your gold atop Mount Dragon!", "class": "no-resize form-control form-control-lg", "rows": 4},
        id="response-field")

    submit = SubmitField(
        "Submit", 
        render_kw={"class": "btn btn-success rounded"},
        id="submit-response")