# Imports
from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, login_user, logout_user, current_user
from app.models import Users, Posts, Responses, GoldChanges, PostChanges # Particular tables to be used
from app import models, forms
from app import db, login_manager
from app.blueprints import main
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
from sqlalchemy import func, or_ , desc # Methods to use when querying database
from urllib.parse import urlparse, urljoin # URL checking
from app.controllers import flash_db_error, try_signup_user, try_login_user, try_post_quest, try_quest_view, try_quest_respond, try_search_quests, try_redeem_gold, try_claim_quest, try_finalise_quest, try_relinquish_claim, try_approve_submission, try_deny_submission, try_private_request, try_cancel_request
from app.controllers import InvalidLogin, AccountAlreadyExists, InvalidAction, InvalidPermissions

###########
# Routes  #
###########
# Please rememeber that the last app.route tag is what the page will be displayed as.

debug = True

# Home page
@main.route("/index")
@main.route("/home")
@main.route("/")
def home():
    # Set display limit on quests
    display_limit = 3

    # Fetch only unclaimed quests in random order
    try:
        quests = db.session.query(Posts) \
            .filter(Posts.claimed == False, Posts.private==False, Posts.deleted==False) \
            .order_by(func.random()) \
            .limit(display_limit) \
            .all()
    except SQLAlchemyError as e:
        flash_db_error(debug, str(e), "Failed loading quests.")
        return render_template("home.html", quests=None, moreQuests=False, unclaimedQuests=False)


    # Check if there are any unclaimed quests to display (could be none)
    moreQuests = len(quests) > display_limit - 1 # True if more quests than can possibly display, False otherwise
    unclaimedQuests = len(quests) > 0  # True if there exists unclaimed quests, False otherwise

    return render_template("home.html", quests=quests, moreQuests=moreQuests, unclaimedQuests=unclaimedQuests)


# If a user tried to access a page they aren't authorised for (not logged in)
@login_manager.unauthorized_handler
def unauthorized():
    # Store the URL the user wanted to access
    next_url = request.url
    flash('Please log in to access this page.', 'danger')
    return redirect(url_for('main.login', next=next_url))


# Login
@main.route("/signup", methods=["POST", "GET"])
@main.route("/login", methods=["POST", "GET"])
def login():
    # Check if user is already logged in
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    is_signup = request.path.endswith('signup') # Determine if linked straight to signup
    login_form = forms.LoginForm()
    signup_form = forms.SignupForm()

    next_page = request.args.get('next')  # Get the next parameter from the URL, if present

    if request.method == 'POST':
        # If user is going somewhere after login/signup
        next_page = request.form.get('next')  # Override with the next parameter from the form

        # If signup form submitted
        if signup_form.validate_on_submit():
            try:
                username = signup_form.username.data
                email = signup_form.email.data
                password = signup_form.password.data
                new_user = try_signup_user(username, email, password)
                login_user(new_user, remember=False) # Assuming dont remember them
                flash('Account created successfully!', 'success')
                if next_page and is_safe_url(next_page):
                    return redirect(next_page) # If user was trying to go somewhere earlier
                return redirect(url_for('main.home'))
            except SQLAlchemyError as e:
                flash_db_error(debug, str(e), "Failed loading user information.")
            except AccountAlreadyExists as e:
                signup_form.username.errors.append(str(e))
            except Exception as e:
                flash_db_error(debug, str(e), "Failed creating an account.")
        
        # If login form submitted
        elif login_form.validate_on_submit():
            try:
                user_info = login_form.login.data
                password = login_form.password.data
                user = try_login_user(user_info, password)
                login_user(user, remember=login_form.remember_me.data)
                flash('Logged in successfully!', 'success')
                if next_page and is_safe_url(next_page):
                    return redirect(next_page) # If user was trying to go somewhere earlier
                return redirect(url_for('main.home'))
            except SQLAlchemyError as e:
                flash_db_error(debug, str(e), "Failed loading user information.")
            except InvalidLogin as e:
                login_form.login.errors.append(str(e))

    return render_template("login.html", login_form=login_form, signup_form=signup_form, is_signup=is_signup, next=next_page)


# User logout
@main.route('/logout', methods=["POST", "GET"])
@login_required
def logout():
    logout_user()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('main.home'))


# Post request
@main.route('/post', methods=["POST", "GET"])
@login_required
def post_quest():
    posting_form = forms.PostForm()
    
    if request.method == 'POST':
        if posting_form.validate_on_submit():
            try:
                try_post_quest(posting_form)
                flash('ReQuest posted successfully!', 'success')
                return redirect(url_for('main.home'))
            except InvalidAction as e:
                flash(str(e), 'danger')
            except Exception as e:
                flash_db_error(debug, str(e), "Failed posting ReQuest.")

    gold = current_user.gold_available # Get user's available gold
    return render_template("posting.html", posting_form=posting_form, gold_available=gold)


# Post request
@main.route('/view', methods=["POST", "GET"])
@login_required
def quest_view():
    try:
        post = try_quest_view(request)
    except Exception as e:
        flash(str(e), 'danger')
        return redirect(url_for('main.home'))
    
    creation_date = post.creationDate.strftime('%Y-%m-%d')
    claim_date = post.claimDate.strftime('%Y-%m-%d') if post.claimDate else None # Get the claim date if it exists
    response_form = forms.ResponseForm()

    if response_form.validate_on_submit():
        try:
            try_quest_respond(post, response_form)
            flash('Response added successfully!', 'success')
            return redirect(url_for('main.quest_view', postID=post.postID)) # Ensure form cant be resubmitted by redirecting user to same page (deletes current form)
        except Exception as e:
            flash_db_error(debug, str(e), "Failed adding response.")

    return render_template('post-view.html', post=post, response_form=response_form, creation_date=creation_date, claim_date=claim_date)


# Leaderboard
@main.route("/leaderboard")
def leaderboard():
    # Variable defines users per page on leaderboard
    page_size = 50
    # Get the current page number
    page_number = int(request.args.get("page", 1)) # Doesn't need error handling
   
    # start index of users for page
    start_index = (page_number - 1) * page_size
    
    try:
        #Query the DB for the username and gold for each user ordered by the users gold count
        leaderboard_users = Users.query.with_entities(Users.username, Users.gold).order_by(desc(Users.gold)).slice(start_index, (start_index + page_size)).all()
        # Find number of users
        total_users = Users.query.count()
    except SQLAlchemyError as e:
        flash_db_error(debug, str(e), "Failed loading users.")
        return redirect(url_for('main.home'))

    #calculate end_index after gettign the leaderboard_users
    end_index = min(start_index + page_size, total_users)
    
    prev_page = page_number - 1 if page_number > 1 else None
    next_page = page_number + 1 if end_index < total_users else None
    
    # Calculate total pages
    total_pages = (total_users + page_size - 1) // page_size
    
    # set the current page number
    current_page = page_number
    
    # render the leaderboard template with necessary datas
    return render_template("leaderboard.html", users=leaderboard_users, start_index=start_index, end_index=end_index, prev_page=prev_page, next_page=next_page, total_users=total_users, total_pages=total_pages, current_page=current_page, page_size=page_size)


# Logs view
@main.route('/logs', methods=["GET"])
@login_required
def logs():
    if not current_user.isAdmin:
        flash('Invalid Permissions.', 'danger')
        return redirect(url_for('main.home'))

    log_type = request.args.get('type', 'requests')  # Default to ReQuest logs
    page_size = 50
    page_number = int(request.args.get("page", 1))
    start_index = (page_number - 1) * page_size

    try:
        if log_type == 'gold':
            logs_query = GoldChanges.query.order_by(GoldChanges.changeDate.desc())
        else:
            logs_query = PostChanges.query.order_by(PostChanges.changeDate.desc())

        total_logs = logs_query.count()
        logs = logs_query.offset(start_index).limit(page_size).all()
    except SQLAlchemyError as e:
        flash_db_error(debug, str(e), "Failed loading logs.")
        return redirect(url_for('main.home'))

    end_index = start_index + len(logs)
    total_pages = (total_logs + page_size - 1) // page_size
    prev_page = page_number - 1 if page_number > 1 else None
    next_page = page_number + 1 if end_index < total_logs else None

    return render_template('logs.html', logs=logs, log_type=log_type, current_page=page_number, total_pages=total_pages, prev_page=prev_page, next_page=next_page, start_index=start_index, end_index=end_index, page_size=page_size)


@main.route("/search", methods=["POST", "GET"])
@login_required
def search():
    searching_form = forms.SearchForm()
    quest_type = request.args.get('type') # No need to check if this fails (handled later)

    try:
        posts = try_search_quests(request, searching_form, quest_type)
    except SQLAlchemyError as e:
        flash_db_error(debug, str(e), "Failed to load ReQuests.")
        return redirect(url_for('main.home'))

    username = current_user.username if quest_type else ""
    title = f"{quest_type.capitalize() if quest_type else 'All'} ReQuests of {username}" if username else "Available ReQuests"

    return render_template("search.html", searching_form=searching_form, posts=posts, title=title, quest_type=quest_type)


@main.route("/gold-farm", methods=["POST", "GET"])
@login_required
def gold_farm():
    if request.method == 'POST':
        try:
            try_redeem_gold(request)
        except Exception as e:
            flash_db_error(debug, str(e), "Failed updating gold.")

    return render_template("gold-farm.html")



# Handle Post Control Panel Buttons
# Claim request
@main.route('/claim_request/<int:post_id>', methods=['POST'])
@login_required
def claim_request(post_id):
    try:
        try_claim_quest(post_id)
        flash('ReQuest claimed successfully!', 'success')
        return jsonify({"message": "ReQuest claimed successfully!"}), 200
    except InvalidAction as e:
        flash(str(e), 'danger')
        return jsonify({"message": "Unable to claim ReQuest."}), 400
    except SQLAlchemyError as e:
        flash_db_error(debug, str(e), "Failed to claim ReQuest.")
        return jsonify({"message": f"Unable to claim ReQuest - Database error."}), 400
    except Exception as e:
        flash_db_error(debug, str(e), "Failed to claim ReQuest.")
        return jsonify({"message": f"Unable to claim ReQuest - Database error."}), 400


# Finalise request
@main.route('/finalise_request/<int:post_id>', methods=['POST'])
@login_required
def finalise_request(post_id):
    try:
        try_finalise_quest(post_id)
        flash('ReQuest submission sent successfully!', 'success')
        return jsonify({"message": "ReQuest finalised successfully!"}), 200
    except InvalidAction as e:
        flash(str(e), 'danger')
        return jsonify({"message": "Unable to finalise ReQuest."}), 400
    except SQLAlchemyError as e:
        flash_db_error(debug, str(e), "Failed to finalise ReQuest.")
        return jsonify({"message": "Unable to finalise ReQuest - Database error."}), 400
    except Exception as e:
        flash_db_error(debug, str(e), "Failed to finalise ReQuest.")
        return jsonify({"message": "Unable to finalise ReQuest - Database error."}), 400


# Relinquish claim
@main.route('/relinquish_claim/<int:post_id>', methods=['POST'])
@login_required
def relinquish_claim(post_id):
    try:
        try_relinquish_claim(post_id)
        flash('Claim on ReQuest relinquished successfully!', 'success')
        return jsonify({"message": "ReQuest claim relinquished successfully!"}), 200
    except InvalidAction as e:
        flash(str(e), 'danger')
        return jsonify({"message": "Unable to relinquish ReQuest claim."}), 400
    except SQLAlchemyError as e:
        flash_db_error(debug, str(e), "Failed to relinquish ReQuest claim.")
        return jsonify({"message": "Unable to relinquish ReQuest claim - Database error."}), 400
    except Exception as e:
        flash_db_error(debug, str(e), "Failed to relinquish ReQuest claim.")
        return jsonify({"message": "Unable to relinquish ReQuest claim - Database error."}), 400


# Approve submission
@main.route('/approve_submission/<int:post_id>', methods=['POST'])
@login_required
def approve_submission(post_id):
    try:
        try_approve_submission(post_id)
        flash('ReQuest submission approved successfully!', 'success')
        return jsonify({"message": "ReQuest submission approved successfully!"}), 200
    except InvalidAction as e:
        flash(str(e), 'danger')
        return jsonify({"message": "Unable to approve ReQuest submission."}), 400
    except SQLAlchemyError as e:
        flash_db_error(debug, str(e), "Failed to approve ReQuest submission.")
        return jsonify({"message": "Unable to approve ReQuest submission - Database error."}), 400
    except Exception as e:
        flash_db_error(debug, str(e), "Failed to approve ReQuest submission.")
        return jsonify({"message": "Unable to approve ReQuest submission - Database error."}), 400


# Deny submission
@main.route('/deny_submission/<int:post_id>', methods=['POST'])
@login_required
def deny_submission(post_id):
    try:
        try_deny_submission(post_id)
        flash('ReQuest submission denied successfully!', 'success')
        return jsonify({"message": "ReQuest submission denied."}), 200
    except InvalidAction as e:
        flash(str(e), 'danger')
        return jsonify({"message": "Unable to deny ReQuest submission."}), 400
    except SQLAlchemyError as e:
        flash_db_error(debug, str(e), "Failed to deny ReQuest submission.")
        return jsonify({"message": "Unable to deny ReQuest submission - Database error."}), 400
    except Exception as e:
        flash_db_error(debug, str(e), "Failed to deny ReQuest submission.")
        return jsonify({"message": "Unable to deny ReQuest submission - Database error."}), 400


# Change request privacy
@main.route('/private_request/<int:post_id>', methods=['POST'])
@login_required
def private_request(post_id):
    try:
        try_private_request(post_id)
        flash('ReQuest privacy changed successfully!', 'success')
        return jsonify({"message": "ReQuest privacy changed successfully."}), 200
    except InvalidAction as e:
        flash(str(e), 'danger')
        return jsonify({"message": "Unable to change ReQuest privacy."}), 400
    except SQLAlchemyError as e:
        flash_db_error(debug, str(e), "Failed to change ReQuest privacy.")
        return jsonify({"message": "Unable to change ReQuest privacy - Database error."}), 400
    except Exception as e:
        flash_db_error(debug, str(e), "Failed to change ReQuest privacy.")
        return jsonify({"message": "Unable to change ReQuest privacy - Database error."}), 400


# Cancel request
@main.route('/cancel_request/<int:post_id>', methods=['POST'])
@login_required
def cancel_request(post_id):
    try:
        try_cancel_request(post_id)
        flash('ReQuest cancelled successfully!', 'success')
        return jsonify({"message": "ReQuest cancelled successfully."}), 200
    except InvalidAction as e:
        flash(str(e), 'danger')
        return jsonify({"message": "Unable to cancel ReQuest."}), 400
    except SQLAlchemyError as e:
        flash_db_error(debug, str(e), "Failed to cancel ReQuest.")
        return jsonify({"message": "Unable to cancel ReQuest - Database error."}), 400
    except Exception as e:
        flash_db_error(debug, str(e), "Failed to cancel ReQuest.")
        return jsonify({"message": "Unable to cancel ReQuest - Database error."}), 400


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc

# Routes to add or remove admin from an account, requires an already logged in user account
@main.route("/admin4meplz", methods=["GET"])
@login_required
def give_admin():
    if current_user.isAdmin:
        flash('User is already an admin!', 'danger')
    else:
        current_user.isAdmin = True
        try:
            db.session.commit()
            flash('You are now an admin!', 'success')
        except Exception as e:
            db.session.rollback()
            if debug:
                flash('Error adding admin to database. {}'.format(e), 'danger')
            else: 
                flash('Failed adding admin. Please try again later or contact staff.', 'danger')
    return redirect(url_for('main.home'))

@main.route("/noadmin4meplz", methods=["GET"])
@login_required
def remove_admin():
    if current_user.isAdmin:
        current_user.isAdmin = False
        try:
            db.session.commit()
            flash('You are no longer an admin.', 'success')
        except Exception as e:
            db.session.rollback()
            if debug:
                flash('Error removing admin from database. {}'.format(e), 'danger')
            else: 
                flash('Failed removing admin. Please try again later or contact staff.', 'danger')
    else:
        flash('User is not an admin!', 'danger')
    return redirect(url_for('main.home'))