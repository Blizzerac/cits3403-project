# Imports
from flask import render_template, request, redirect, url_for, flash
from flask_bcrypt import bcrypt
from app.models import Users # The user table in the database
from app import models, forms
from app import app, bcrypt, db
from datetime import datetime


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
    login_form = forms.LoginForm()
    signup_form = forms.SignupForm()

    # If signup form submitted
    if signup_form.validate_on_submit():
        hashed_pass = bcrypt.generate_password_hash(signup_form.password.data)
        new_user = Users(username=signup_form.username.data, email=signup_form.email.data, password=hashed_pass)
        db.session.add(new_user)
        # Try commit new user to database.
        try:
            db.session.commit()
            flash('Account created successfully', 'success')
            return redirect(url_for('home'))
        # If failed, rollback database and warn user.
        except Exception as e:
            db.session.rollback()
            flash('Error adding user to database. {}'.format(e), 'error')
        
    return render_template("login.html", login_form=login_form, signup_form=signup_form)

# Leaderboard
@app.route("/leaderboard")
def leaderboard():
    return render_template("leaderboard.html")