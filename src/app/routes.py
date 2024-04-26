# Imports
from flask import *
from app import app


###########
# Routes  #
###########
# Please rememeber that the last app.route tag is what the page will be displayed as.

# Hardcoded user data for leaderboard testing purposes
leaderboard_users = [
    {"username": f"User {i+1}", "quests_complete": 1000 - i} for i in range(1000)
]



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
    return render_template("login.html")

# Leaderboard
@app.route("/leaderboard")
def leaderboard():
    return render_template("leaderboard.html", users=leaderboard_users)

@app.route("/search")
def search():
    return render_template("search.html")