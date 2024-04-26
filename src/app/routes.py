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
    return render_template("login.html")

# Leaderboard
@app.route("/leaderboard")
def leaderboard():
    # Hardcoded user data for leaderboard testing purposes
    leaderboard_users = [
        {"username": f"User {i+1}", "quests_complete": 10000 - i} for i in range(10000)
    ]
    page_size = 100 
    page_number = int(request.args.get("page", 1))  
    
    start_index = (page_number - 1) * page_size
    end_index = min(start_index + page_size, len(leaderboard_users))
    
    prev_page = page_number - 1 if page_number > 1 else None
    next_page = page_number + 1 if end_index < len(leaderboard_users) else None
    
    total_users = len(leaderboard_users)
    total_pages = (total_users + page_size - 1) // page_size
    current_page = page_number
    
    return render_template("leaderboard.html", users=leaderboard_users[start_index:end_index], start_index=start_index, end_index=end_index, prev_page=prev_page, next_page=next_page, total_users=total_users, total_pages=total_pages, current_page=current_page, page_size=page_size)


@app.route("/search")
def search():
    return render_template("search.html")