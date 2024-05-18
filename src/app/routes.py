# Imports
from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, login_user, logout_user, current_user
from app.models import Users, Posts, Responses # Particular tables to be used
from app import models, forms
from app import flaskApp, db, login_manager
from datetime import datetime
from sqlalchemy import func, or_ , desc # Methods to use when querying database
from urllib.parse import urlparse, urljoin # URL checking

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
    # Set display limit on quests
    DISPLAY_LIMIT = 3

    # Fetch only unclaimed quests in random order
    quests = db.session.query(Posts) \
        .filter(Posts.claimed == False, Posts.private==False) \
        .order_by(func.random()) \
        .limit(DISPLAY_LIMIT) \
        .all()

    # Check if there are any unclaimed quests to display
    moreQuests = len(quests) > DISPLAY_LIMIT-1 # True if more quests than can possibly display, False otherwise
    unclaimedQuests = len(quests) > 0  # True if there exists unclaimed quests, False otherwise

    return render_template("home.html", quests=quests, moreQuests=moreQuests, unclaimedQuests=unclaimedQuests)


# If a user tried to access a page they aren't authorised for (not logged in)
@login_manager.unauthorized_handler
def unauthorized():
    # Store the URL the user wanted to access
    next_url = request.url
    flash('Please log in to access this page.', 'danger')
    return redirect(url_for('login', next=next_url))



# If a user tried to access a page they aren't authorised for (not logged in)
@login_manager.unauthorized_handler
def unauthorized():
    # Store the URL the user wanted to access
    next_url = request.url
    flash('Please log in to access this page.', 'danger')
    return redirect(url_for('login', next=next_url))


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

    next_page = request.args.get('next')  # Get the next parameter from the URL, if present

    if request.method == 'POST':
        # If user is going somewhere after login/signup
        next_page = request.form.get('next')  # Override with the next parameter from the form

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
                    if next_page and is_safe_url(next_page):
                        return redirect(next_page) # If user was trying to go somewhere earlier
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
                if next_page and is_safe_url(next_page):
                    return redirect(next_page) # If user was trying to go somewhere earlier
                return redirect(url_for('dashboard'))
            else:
                # Dont inform the user if the account or password is incorrect (security flaw) - only general error
                login_form.login.errors.append('Incorrect account details.')

        # # If login fails with errors, return to login form
        # elif not login_form.validate_on_submit() and request.method == 'POST':
        #     return render_template("login.html", login_form=login_form, signup_form=signup_form, is_signup=False)

    return render_template("login.html", login_form=login_form, signup_form=signup_form, is_signup=is_signup, next=next_page)


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


# Post request
@flaskApp.route('/view', methods=["POST", "GET"])
@login_required
def quest_view():
    # If no postID given, return user to the home screen
    post_id = request.args.get('postID') # Get the post ID to show
    if not post_id:
        flash('Incorrect usage.', 'danger')
        return redirect(url_for('home'))
    
    # If no post exists, return user to home screen
    post = Posts.query.get(post_id)
    if not post:
        flash('ReQuest does not exist.', 'danger')
        return redirect(url_for('home'))
    if post.private and not (current_user.userID == post.claimerID or current_user.userID == post.posterID):
        flash('Cant acces private ReQuest.', 'danger')
        return redirect(url_for('home'))
    
    creation_date = post.creationDate.strftime('%Y-%m-%d')
    claim_date = post.claimDate.strftime('%Y-%m-%d') if post.claimDate else None # Get the claim date if it exists
    response_form = forms.ResponseForm()

    if response_form.validate_on_submit():
        # Add the response to the database
        new_response = Responses(
            responderID=current_user.userID,
            postID=post.postID,
            msg=response_form.response.data
        )
        db.session.add(new_response)
        try:
            db.session.commit()
        # If failed, rollback database and warn user.
        except Exception as e:
            db.session.rollback()
            if debug:
                flash('Error adding response to database. {}'.format(e), 'danger')
            else: 
                flash('Failed adding response. Please try again later or contact staff.', 'danger')

        # Update posts
        flash('Response added successfully!', 'success')
        return redirect(url_for('quest_view', postID=post.postID)) # Ensure form cant be resubmitted by redirecting user to same page (deletes current form)


    return render_template('post-view.html', post=post, response_form=response_form, creation_date=creation_date, claim_date=claim_date)


# Leaderboard
@flaskApp.route("/leaderboard")
def leaderboard():
    # Variable defines users per page on leaderboard
    page_size = 2
    # Get the current page number
    page_number = int(request.args.get("page", 1))  
   
    # start and end index of users for page
    start_index = (page_number - 1) * page_size
    end_index = start_index + page_size
    
    #Query the DB for the username and gold for each user ordered by the users gold count
    leaderboard_users = Users.query.with_entities(Users.username, Users.gold).order_by(desc(Users.gold)).slice(start_index, end_index).all()
    
    end_index = min(start_index + page_size, len(leaderboard_users))
    
    # calcualte which page number is prev and next (if they exist)
    prev_page = page_number - 1 if page_number > 1 else None
    next_page = page_number + 1 if end_index < len(leaderboard_users) else None
    
    # calculate total users and total pages
    total_users = Users.query.count()
    total_pages = (total_users + page_size - 1) // page_size
    
    # set the current page number
    current_page = page_number
    
    # render the leaderboard template with necessary datas
    return render_template("leaderboard.html", users=leaderboard_users, start_index=start_index, end_index=end_index, prev_page=prev_page, next_page=next_page, total_users=total_users, total_pages=total_pages, current_page=current_page, page_size=page_size)


@flaskApp.route("/search", methods=["POST", "GET"])
@login_required
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
        base_query = Posts.query.filter(Posts.claimed==False, Posts.posterID != current_user.userID, Posts.completed==False, Posts.private==False) # Complex inequality query, default

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

@flaskApp.route("/gold-farm", methods=["POST", "GET"])
@login_required
def gold_farm():
    if request.method == 'POST':
        data = request.get_json()
        coinsToAdd = data['coins']
        try:
            current_user.add_gold(coinsToAdd)
            db.session.commit()
            flash('You earned ' + str(coinsToAdd) + 'g!', 'success')
        
        except Exception as e:
            db.session.rollback()
            if flaskApp.debug:
                flash('Error giving gold. {}'.format(e), 'danger')
            else: 
                flash('ERROR.', 'danger')

    return render_template("gold-farm.html")



# Handle Post Control Panel Buttons

@flaskApp.route('/claim_request/<int:post_id>', methods=['POST'])
@login_required
def claim_request(post_id):
    post = Posts.query.get(post_id)
    if post and not post.claimed and current_user.userID != post.posterID:
        post.claimed = True
        post.claimerID = current_user.userID
        post.claimDate = datetime.now()
        try:
            db.session.commit()
            flash('ReQuest claimed successfully!', 'success')
            return jsonify({"message": "ReQuest claimed successfully!"}), 200
        except Exception as e:
            db.session.rollback()
            flash_fail_ReQuestModify(e)
            return jsonify({"message": f"Unable to claim ReQuest - Database error."}), 400
        
    flash('Unable to claim ReQuest. Is it already claimed?', 'danger')
    return jsonify({"message": "Unable to claim ReQuest."}), 400


@flaskApp.route('/finalise_request/<int:post_id>', methods=['POST'])
@login_required
def finalise_request(post_id):
    post = Posts.query.get(post_id)
    if post and post.claimed and current_user.userID == post.claimerID and not post.waitingApproval:
        post.waitingApproval = True
        try:
            db.session.commit()
            flash('ReQuest submission sent successfully!', 'success')
            return jsonify({"message": "ReQuest finalised successfully!"}), 200
        except Exception as e:
            db.session.rollback()
            flash_fail_ReQuestModify(e)
            return jsonify({"message": f"Unable to finalise ReQuest - Database error."}), 400
    
    flash('Unable to send ReQuest submission. Have you claimed it?', 'danger')
    return jsonify({"message": "Unable to finalise ReQuest."}), 400


@flaskApp.route('/relinquish_claim/<int:post_id>', methods=['POST'])
@login_required
def relinquish_claim(post_id):
    post = Posts.query.get(post_id)
    if post and post.claimed and current_user.userID == post.claimerID:
        post.claimed = False # Reset claim
        post.claimerID = None
        post.claimDate = None
        post.waitingApproval = False # Ensure reset this value (can cause bug if left)
        post.private = False # Ensure others can claim it
        try:
            db.session.commit()
            flash('Claim on ReQuest reliquished successfully!', 'success')
            return jsonify({"message": "ReQuest claim relinquished successfully!"}), 200
        except Exception as e:
            db.session.rollback()
            flash_fail_ReQuestModify(e)
            return jsonify({"message": f"Unable to relinquish ReQuest claim - Database error."}), 400
        
    flash('Unable relinquish ReQuest claim. Have you claimed it?', 'danger')
    return jsonify({"message": "Unable to relinquish ReQuest claim."}), 400


@flaskApp.route('/approve_submission/<int:post_id>', methods=['POST'])
@login_required
def approve_submission(post_id):
    post = Posts.query.get(post_id)
    if post and post.waitingApproval and current_user.userID == post.posterID:
        post.completed = True
        post.waitingApproval = False
        gold = post.reward
        claimer = Users.query.get(post.claimerID)
        if not claimer:
            flash('Could not find claimer in database.', 'danger')
            return jsonify({"message": f"Could not find claimer in database."}), 400
        
        try:
            # Check if it correctly got the user
            claimer.add_gold(gold)
            current_user.quest_payout(gold)
            db.session.commit()
            flash('ReQuest submission approved successfully!', 'success')
            return jsonify({"message": "ReQuest submission approved successfully!"}), 200
        except Exception as e:
            db.session.rollback()
            flash_fail_ReQuestModify(e)
            return jsonify({"message": f"Unable to approve ReQuest submission - Database error."}), 400
        
    flash('Unable approve ReQuest submission claim. Has it been submitted for approval?', 'danger')
    return jsonify({"message": "Unable to approve ReQuest submission."}), 400


@flaskApp.route('/deny_submission/<int:post_id>', methods=['POST'])
@login_required
def deny_submission(post_id):
    post = Posts.query.get(post_id)
    if post and post.waitingApproval and current_user.userID == post.posterID:
        post.waitingApproval = False
        try:
            db.session.commit()
            flash('ReQuest submission denied successfully!', 'success')
            return jsonify({"message": "ReQuest submission denied."}), 200
        except Exception as e:
            db.session.rollback()
            flash_fail_ReQuestModify(e)
            return jsonify({"message": f"Unable to deny ReQuest submission - Database error."}), 400
        
    flash('Unable deny ReQuest submission claim. Has it been submitted for approval?', 'danger')
    return jsonify({"message": "Unable to deny submission."}), 400


@flaskApp.route('/private_request/<int:post_id>', methods=['POST'])
@login_required
def private_request(post_id):
    post = Posts.query.get(post_id)
    if post and post.claimed and current_user.userID == post.posterID:
        try:
            post.private = not post.private # Swap private boolean field
            db.session.commit()
            flash('ReQuest privacy changed successfully!', 'success')
            return jsonify({"message": "ReQuest privacy changed successfully."}), 200
        except Exception as e:
            db.session.rollback()
            flash_fail_ReQuestModify(e)
            return jsonify({"message": f"Unable to change ReQuest privacy - Database error."}), 400
        
    flash('Unable to change ReQuest privacy. Is it claimed?', 'danger')
    return jsonify({"message": "Unable to change ReQuest privacy."}), 400


@flaskApp.route('/cancel_request/<int:post_id>', methods=['POST'])
@login_required
def cancel_request(post_id):
    post = Posts.query.get(post_id)
    if post and not post.completed and current_user.userID == post.posterID:
        gold = post.reward
        try:
            current_user.quest_refund(gold)
            db.session.delete(post)
            db.session.commit()
            flash('ReQuest cancelled successfully!', 'success')
            return jsonify({"message": "ReQuest cancelled successfully."}), 200
        except Exception as e:
            db.session.rollback()
            flash_fail_ReQuestModify(e)
            return jsonify({"message": f"Unable to cancel ReQuest - Database error."}), 400
        
    flash('Unable cancel ReQuest. Do you own it?', 'danger')
    return jsonify({"message": "Unable to cancel ReQuest."}), 400


def flash_fail_ReQuestModify(error):
    if debug:
        flash('Error adjusting ReQuest in database. {}'.format(error), 'danger')
    else: 
        flash('Failed adjusting ReQuest. Please try again later or contact staff.', 'danger')


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc





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