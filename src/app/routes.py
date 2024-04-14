# Imports
from flask import *
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
@app.route("/login")
def login():
    return render_template("log-in.html")