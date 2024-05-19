# Imports
from flask import flash
from flask_login import login_required, login_user, logout_user, current_user
from app.models import Users, Posts, Responses, GoldChanges, PostChanges # Particular tables to be used
from app import models, forms
from app import db
from sqlalchemy import func, or_ , desc
from sqlalchemy.exc import SQLAlchemyError

# Errors to raise
class DatabaseError(Exception):
    pass

class InvalidLogin(Exception):
    pass

class AccountAlreadyExists(Exception):
    pass

def flash_db_error(debug, error, msg):
    if debug:
        flash(f'Database error: {error}', 'danger')
    else: 
        flash(f'{msg} Please try again later or contact staff.', 'danger')
    
def try_signup_user(signup_form):
    try:
        existing_user = Users.query.filter_by(username=signup_form.username.data).first()
        existing_email = Users.query.filter_by(email=signup_form.email.data.lower()).first() # MUST lower email (case insensitive)
    except SQLAlchemyError as e:
        raise e

    # Check for existing users
    if existing_user:
        raise AccountAlreadyExists('Username is already taken.')
    if existing_email:
        raise AccountAlreadyExists('An account with this email already exists.')

    if not existing_user and not existing_email:
        new_user = Users(username=signup_form.username.data, email=signup_form.email.data.lower())
        new_user.set_password(signup_form.password.data)
        db.session.add(new_user)
        # Try commit new user to database.
        try:
            db.session.commit()
            login_user(new_user, remember=False) # Assuming dont remember them
            flash('Account created successfully!', 'success')
        # If failed, rollback database and warn user.
        except Exception as e:
            db.session.rollback()
            raise e
        
def try_login_user(login_form):
    user_input = login_form.login.data
    # Determine if the input is an email or username
    try:
        if "@" in user_input:
            user = Users.query.filter_by(email=user_input.lower()).first() # MUST lower email to remain case insensitive
        else:
            user = Users.query.filter_by(username=user_input).first()
    except SQLAlchemyError as e:
        raise e

    # Check password hash and login
    if user and user.check_password(login_form.password.data):
        login_user(user, remember=login_form.remember_me.data)
        flash('Logged in successfully!', 'success')
    else:
        raise InvalidLogin("Incorrect account details.")
