# Imports
from flask import render_template, request, redirect, url_for, flash
from flask_bcrypt import bcrypt
from app.models import User # The user table in the database
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
        new_user = User(username=signup_form.username.data, email=signup_form.email.data, password=hashed_pass)
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
    # Hardcoded user data for leaderboard testing purposes
    # Replace this with link to DB at later point
    leaderboard_users = [
        {"username": f"User {i+1}", "quests_complete": 10000 - i} for i in range(10000)
    ]
    
    # Variable defines users per page on leaderboard
    page_size = 50
    # Get the current page number
    page_number = int(request.args.get("page", 1))  
    
    # start and end index of users for page
    start_index = (page_number - 1) * page_size
    end_index = min(start_index + page_size, len(leaderboard_users))
    
    # calcualte which page number is prev and next (if they exist)
    prev_page = page_number - 1 if page_number > 1 else None
    next_page = page_number + 1 if end_index < len(leaderboard_users) else None
    
    # calculate total users and total pages
    total_users = len(leaderboard_users)
    total_pages = (total_users + page_size - 1) // page_size
    
    # set the current page number
    current_page = page_number
    
    # render the leaderboard template with necessary datas
    return render_template("leaderboard.html", users=leaderboard_users[start_index:end_index], start_index=start_index, end_index=end_index, prev_page=prev_page, next_page=next_page, total_users=total_users, total_pages=total_pages, current_page=current_page, page_size=page_size)


@app.route("/search")
def search():
    searching_form = forms.SearchForm()

    # example post data, hardcoded for now
    posts = [
        {"title": "Post 1", "description": "Description of post 1"},
        {"title": "Post 2", "description": "Description of post 2"},
        {"title": "Post 3", "description": "Description of post 3"},
        {"title": "Post 4", "description": "Description of post 4"},
        {"title": "Post 5", "description": "Description of post 5"},
        {"title": "Post 6", "description": "Description of post 6. Further description of post 6 to illustrate the dynamic nature of this div"}
    ]

    return render_template("search.html", searching_form=searching_form, posts=posts)

@app.route("/posting", methods=["POST", "GET"])
def posting():
    posting_form = forms.PostForm()
    return render_template("posting.html", posting_form=posting_form)