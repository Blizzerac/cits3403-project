# Imports
from flask import *
from app import app


###########
# Routes  #
###########
# Please rememeber that the last app.route tag is what the page will be displayed as.

# Hardcoded user data for leaderboard testing purposes
leaderboard_users = [
    {"username": "User 1", "quests_complete": 10},
    {"username": "User 2", "quests_complete": 8},
    {"username": "User 3", "quests_complete": 7},
    {"username": "User 4", "quests_complete": 6},
    {"username": "User 5", "quests_complete": 5},
    {"username": "User 6", "quests_complete": 4},
    {"username": "User 7", "quests_complete": 3},
    {"username": "User 8", "quests_complete": 2},
    {"username": "User 9", "quests_complete": 1},
    {"username": "User 10", "quests_complete": 0},
    {"username": "User 11", "quests_complete": 0},
    {"username": "User 12", "quests_complete": 0},
    {"username": "User 13", "quests_complete": 0},
    {"username": "User 14", "quests_complete": 0},
    {"username": "User 15", "quests_complete": 0},
    {"username": "User 16", "quests_complete": 0},
    {"username": "User 17", "quests_complete": 0},
    {"username": "User 18", "quests_complete": 0},
    {"username": "User 19", "quests_complete": 0},
    {"username": "User 20", "quests_complete": 0}
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