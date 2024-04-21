# Imports
from flask import render_template, request, redirect, url_for
from app import app, models, forms


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
    return render_template("login.html", login_form=login_form, signup_form=signup_form)

# Leaderboard
@app.route("/leaderboard")
def leaderboard():
    return render_template("leaderboard.html")