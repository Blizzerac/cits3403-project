# Imports
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, login_user, logout_user, current_user
from app.models import Users, Posts # Particular tables to be used
from app import models, forms
from app import flaskApp, db
from sqlalchemy.sql.expression import func, or_ # Methods to use when querying database

###########
# Routes  #
###########
# Please rememeber that the last app.route tag is what the page will be displayed as.


# Home page
@flaskApp.route("/index")
@flaskApp.route("/home")
@flaskApp.route("/")
def home():
    # Set display limit on quests
    DISPLAY_LIMIT = 3

    # Fetch only unclaimed quests in random order
    quests = db.session.query(Posts) \
        .filter(Posts.claimed == False) \
        .order_by(func.random()) \
        .limit(DISPLAY_LIMIT) \
        .all()

    # Check if there are any unclaimed quests to display
    moreQuests = len(quests) > DISPLAY_LIMIT-1 # True if more quests than can possibly display, False otherwise
    unclaimedQuests = len(quests) > 0  # True if there exists unclaimed quests, False otherwise

    return render_template("home.html", quests=quests, moreQuests=moreQuests, unclaimedQuests=unclaimedQuests)

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
            existing_email = Users.query.filter_by(email=signup_form.email.data.lower()).first() # MUST lower email (case insensitive)

            # Check for existing users
            if existing_user:
                signup_form.username.errors.append('Username is already taken.')
            if existing_email:
                signup_form.email.errors.append('An account with this email already exists.')

            if not existing_user and not existing_email:
                new_user = Users(username=signup_form.username.data, email=signup_form.email.data.lower())
                new_user.set_password(signup_form.password.data)
                db.session.add(new_user)
                # Try commit new user to database.
                try:
                    db.session.commit()
                    login_user(new_user, remember=False) # Assuming dont remember them
                    flash('Account created successfully!', 'success')
                    return redirect(url_for('home'))
                # If failed, rollback database and warn user.
                except Exception as e:
                    db.session.rollback()
                    if flaskApp.debug:
                        flash('Error adding user to database. {}'.format(e), 'danger')
                    else: 
                        flash('Failed creating an account. Please try again later or contact staff.', 'danger')
        
        # If login form submitted
        elif login_form.validate_on_submit():
            user_input = login_form.login.data
            # Determine if the input is an email or username
            if "@" in user_input:
                user = Users.query.filter_by(email=user_input.lower()).first() # MUST lower email to remain case insensitive
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
        if posting_form.validate_on_submit():
            # Check if a user has enough gold & user's available gold
            if not current_user.quest_create(posting_form.post_reward.data):
                flash('Not enough gold to uphold the reward!', 'danger')
            
            else:
                try:
                    new_post = Posts(posterID=current_user.userID, title=posting_form.post_name.data, description=posting_form.post_description.data, reward=posting_form.post_reward.data)
                    db.session.add(new_post)
                    db.session.commit()
                    flash('ReQuest posted successfully!', 'success')
                    return redirect(url_for('home'))
            
                except Exception as e:
                    db.session.rollback()
                    if flaskApp.debug:
                        flash('Error adding ReQuest to database. {}'.format(e), 'danger')
                    else: 
                        flash('Failed posting ReQuest. Please try again later or contact staff.', 'danger')

    gold = current_user.gold_available # Get user's available gold
    return render_template("posting.html", posting_form=posting_form, gold_available=gold)


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


@flaskApp.route("/search", methods=["POST", "GET"])
def search():
    searching_form = forms.SearchForm()
    quest_type = request.args.get('type')

    # Determine the base query based on user and quest type
    if quest_type == 'active':
        base_query = Posts.query.filter_by(posterID=current_user.userID, completed=False)  # Active quests posted by the user
    elif quest_type == 'claimed':
        base_query = Posts.query.filter_by(claimerID=current_user.userID, claimed=True, completed=False)  # Claimed quests by the user, not yet completeds
    elif quest_type == 'completed':
        base_query = Posts.query.filter_by(claimerID=current_user.userID, completed=True)  # Completed quests by the user
    elif quest_type == 'inactive':
        base_query = Posts.query.filter(Posts.posterID == current_user.userID, Posts.completed==True, Posts.claimerID != current_user.userID) # Complex inequality query, completed quests by others posted by user
    else:
        base_query = Posts.query.filter(Posts.claimed==False, Posts.posterID != current_user.userID, Posts.completed==False) # Complex inequality query, default

    # Searching or showing all
    if request.method == 'POST' and searching_form.validate_on_submit():
        if 'show_all' in request.form:
            posts = base_query.all()
        else:
            search_query = searching_form.post_search_name.data
            posts = base_query.filter(
                or_(
                    Posts.title.contains(search_query),
                    Posts.description.contains(search_query)
                )
            ).all()
    # GET request for page
    else:
        posts = base_query.all()

    username = current_user.username if quest_type else ""
    title = f"{quest_type.capitalize() if quest_type else 'All'} ReQuests of {username}" if username else "Available ReQuests"

    return render_template("search.html", searching_form=searching_form, posts=posts, title=title, quest_type=quest_type)




# THIS ROUTE MUST BE REMOVED -- ONLY FOR DEVELOPMENT PURPOSES
@flaskApp.route("/givegold")
@login_required
def giveGold():
    try:
        current_user.add_gold(500)
        db.session.commit()
        flash('Given user 500 gold.', 'success')
    
    except Exception as e:
        db.session.rollback()
        if flaskApp.debug:
            flash('Error giving gold. {}'.format(e), 'danger')
        else: 
            flash('ERROR.', 'danger')
    
    return redirect(url_for('home'))
