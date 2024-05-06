# Imports
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, login_user, logout_user, current_user
from flask_bcrypt import bcrypt
from app.models import Users # The user table in the database
from app import models, forms
from app import app, bcrypt, db
from datetime import datetime

# Settings
debug = True


###########
# Routes  #
###########
# Please rememeber that the last app.route tag is what the page will be displayed as.

# Home page
@app.route("/index")
@app.route("/home")
@app.route("/")
def home():
    return render_template("home.html")

# Login
@app.route("/signup", methods=["POST", "GET"])
@app.route("/login", methods=["POST", "GET"])
def login():
    # Check if user is already logged in
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    is_signup = request.path.endswith('signup') # Determine if linked straight to signup
    login_form = forms.LoginForm()
    signup_form = forms.SignupForm()

    # If signup form submitted
    if signup_form.validate_on_submit():
        existing_user = Users.query.filter_by(username=signup_form.username.data).first()
        existing_email = Users.query.filter_by(email=signup_form.email.data).first()

        # Check for existing users
        if existing_user:
            signup_form.username.errors.append('Username is already taken.')
        if existing_email:
            signup_form.email.errors.append('An account with this email already exists.')

        if not existing_user and not existing_email:
            hashed_pass = bcrypt.generate_password_hash(signup_form.password.data).decode('utf-8')
            new_user = Users(username=signup_form.username.data, email=signup_form.email.data, password=hashed_pass)
            db.session.add(new_user)
            # Try commit new user to database.
            try:
                db.session.commit()
                login_user(new_user,remember=False) # Assuming dont remember them
                flash('Account created successfully!', 'success')
                return redirect(url_for('home'))
            # If failed, rollback database and warn user.
            except Exception as e:
                db.session.rollback()
                if debug:
                    flash('Error adding user to database. {}'.format(e), 'danger')
                else: 
                    flash('Error adding user to database.', 'danger')

    # If signup form submission fails with errors, return to signup form
    elif not signup_form.validate_on_submit() and request.method == 'POST':
        return render_template("login.html", login_form=login_form, signup_form=signup_form, is_signup=True)
    
    # If login form submitted
    if login_form.validate_on_submit():
        user_input = login_form.login.data
        # Determine if the input is an email or username
        if "@" in user_input:
            user = Users.query.filter_by(email=user_input).first()
        else:
            user = Users.query.filter_by(username=user_input).first()

        # Check password hash and login
        if user and bcrypt.check_password_hash(user.password, login_form.password.data):
            login_user(user, remember=login_form.remember_me.data)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('dashboard'))
        else:
            login_form.login.errors.append('Incorrect account details.')

    # If login fails with errors, return to login form
    elif not login_form.validate_on_submit() and request.method == 'POST':
        return render_template("login.html", login_form=login_form, signup_form=signup_form, is_signup=False)

    return render_template("login.html", login_form=login_form, signup_form=signup_form, is_signup=is_signup)

# User logout
@app.route('/logout', methods=["POST", "GET"])
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

# User dashboard
@app.route('/dashboard', methods=["POST", "GET"])
@login_required
def dashboard():
    return render_template('home.html') #TEMP UNTIL DASH FINISHED

# Post request
@app.route('/post', methods=["POST", "GET"])
@login_required
def post_quest():
    return render_template('home.html') # TEMP UNTIL COMPLETED

# Leaderboard
@app.route("/leaderboard")
def leaderboard():
    return render_template("leaderboard.html")