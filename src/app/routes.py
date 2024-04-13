# Imports
from flask import *
from app import app


###########
# Routes  #
###########

# Home page
@app.route("/")
@app.route("/index")
def home():
    return render_template("index.html")

# Login
@app.route("/login")
@app.route("/signup")
def login():
    return render_template("log-in.html")