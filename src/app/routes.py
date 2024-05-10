# Imports
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, login_user, logout_user, current_user
from app.models import Users, Posts # The user table in the database
from app import models, forms
from app import flaskApp, db
from datetime import datetime

# Settings
debug = True


###########
# Routes  #
###########
# Please rememeber that the last app.route tag is what the page will be displayed as.


# Home page
@flaskApp.route("/index")
@flaskApp.route("/home")
@flaskApp.route("/")
def home():
    if db.session.query(Posts).count() > 10:
        questCount = True
    else:
        questCount = False
    quests = db.session.query(Posts).limit(10).all()
    return render_template("home.html", quests=quests, questCount=questCount)

# Login
@flaskApp.route("/signup", methods=["POST", "GET"])
@flaskApp.route("/login", methods=["POST", "GET"])
def login():
    # Check if user is already logged in
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    is_signup = request.path.endswith('signup') # Determine if linked straight to signup
    login_form = forms.LoginForm()
    signup_form = forms.SignupForm()

    if request.method == 'POST':
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
                new_user = Users(username=signup_form.username.data, email=signup_form.email.data)
                new_user.set_password(signup_form.password.data)
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
                        flash('Failed creating an account. Please try again later or contact staff.', 'danger')
        
        # If login form submitted
        elif login_form.validate_on_submit():
            user_input = login_form.login.data
            # Determine if the input is an email or username
            if "@" in user_input:
                user = Users.query.filter_by(email=user_input).first()
            else:
                user = Users.query.filter_by(username=user_input).first()

            # Check password hash and login
            if user and user.check_password(login_form.password.data):
                login_user(user, remember=login_form.remember_me.data)
                flash('Logged in successfully!', 'success')
                return redirect(url_for('dashboard'))
            else:
                # Dont inform the user if the account or password is incorrect (security flaw) - only general error
                login_form.login.errors.append('Incorrect account details.')

        # # If login fails with errors, return to login form
        # elif not login_form.validate_on_submit() and request.method == 'POST':
        #     return render_template("login.html", login_form=login_form, signup_form=signup_form, is_signup=False)

    return render_template("login.html", login_form=login_form, signup_form=signup_form, is_signup=is_signup)

# User logout
@flaskApp.route('/logout', methods=["POST", "GET"])
@login_required
def logout():
    logout_user()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('home'))

# User dashboard
@flaskApp.route('/dashboard', methods=["POST", "GET"])
@login_required
def dashboard():
    return render_template('home.html') #TEMP UNTIL DASH FINISHED

# Post request
@flaskApp.route('/post', methods=["POST", "GET"])
@login_required
def post_quest():
    posting_form = forms.PostForm()
    
    if request.method == 'POST':
        print("quest posted")
        if posting_form.validate_on_submit():
            print("quest validated")
            new_post = Posts(posterID=current_user.userID, title=posting_form.post_name.data, description=posting_form.post_description.data)
            db.session.add(new_post)
            try:
                print("quest added")
                db.session.commit()
                flash('Quest posted successfully!', 'success')
                return redirect(url_for('home'))
            except Exception as e:
                db.session.rollback()
                if debug:
                    flash('Error adding quest to database. {}'.format(e), 'danger')
                else: 
                    flash('Failed posting quest. Please try again later or contact staff.', 'danger')
        print("quest not validated")

    return render_template("posting.html", posting_form=posting_form)


# Leaderboard
@flaskApp.route("/leaderboard")
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


@flaskApp.route("/search")
def search():
    searching_form = forms.SearchForm()

    # example post data, hardcoded for now
    posts = [
        {"title": "Post 1", "description": "Description of post 1", "reward": "20 gold"},
        {"title": "Post 2", "description": "Description of post 2", "reward": "30 gold"},
        {"title": "Post 3", "description": "Description of post 3", "reward": "250 gold"},
        {"title": "Post 4", "description": "Description of post 4", "reward": "210 gold"},
        {"title": "Post 5", "description": "Description of post 5", "reward": "220 gold"},
        {"title": "Post 6", "description": "Description of post 6. Further description of post 6 to illustrate the dynamic nature of this div", "reward": "200 gold"}
    ]

    return render_template("search.html", searching_form=searching_form, posts=posts)

@flaskApp.route("/posting", methods=["POST", "GET"])
def posting():
    posting_form = forms.PostForm()
    return render_template("posting.html", posting_form=posting_form)