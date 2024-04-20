# Imports
from flask import render_template, request, redirect, url_for
from app import app


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
@app.route("/signup")
@app.route("/login", methods=["POST", "GET"])
def login():
    return render_template("login.html")

# Leaderboard
@app.route("/leaderboard")
def leaderboard():
    return render_template("leaderboard.html")