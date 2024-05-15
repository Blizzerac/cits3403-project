# Imports
from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, login_user, logout_user, current_user
from app.models import Users, Posts, Responses # Particular tables to be used
from app import models, forms
from app import flaskApp, db
from datetime import datetime
from sqlalchemy import or_  # To search for titles or descriptions when searching

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
    return render_template("home.html")


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
                    if debug:
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
    return redirect(url_for('home'))


# User dashboard
@flaskApp.route('/dashboard', methods=["POST", "GET"])
@login_required
def dashboard():
    return render_template('home.html') #TEMP UNTIL DASH FINISHED


# Post request
@flaskApp.route('/view', methods=["POST", "GET"])
@login_required
def post_quest():
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
    
    creation_date = post.creationDate.strftime('%Y-%m-%d')
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
        return redirect(url_for('post_quest', postID=post.postID)) # Ensure form cant be resubmitted by redirecting user to same page (deletes current form)


    return render_template('post-view.html', post=post, response_form=response_form, date=creation_date)


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

    if request.method == 'POST' and searching_form.validate_on_submit():
        # If the show all button is pressed
        if searching_form.show_all.data:
            posts = Posts.query.all()
        # If we are searching for a post, filter
        else:
            search_query = searching_form.post_search_name.data
            posts = Posts.query.filter(
                or_(
                    Posts.title.contains(search_query),
                    Posts.description.contains(search_query)
                )
            ).all()
    # Otherwise get every post for a get request
    else:
        posts = Posts.query.all()

    return render_template("search.html", searching_form=searching_form, posts=posts)


@flaskApp.route("/posting", methods=["POST", "GET"])
def posting():

    #need to add post and get conditions here

    posting_form = forms.PostForm()
    return render_template("posting.html", posting_form=posting_form)


# Handle Post Control Panel Buttons
@flaskApp.route('/claim_request/<int:post_id>', methods=['POST'])
@login_required
def claim_request(post_id):
    post = Posts.query.get(post_id)
    if post and not post.claimed and current_user.userID != post.posterID:
        post.claimed = True
        post.claimerID = current_user.userID
        #claim date
        db.session.commit()
        return jsonify({"message": "ReQuest claimed successfully!"}), 200
    return jsonify({"message": "Unable to claim ReQuest."}), 400

@flaskApp.route('/finalise_request/<int:post_id>', methods=['POST'])
@login_required
def finalise_request(post_id):
    post = Posts.query.get(post_id)
    if post and post.claimed and current_user.userID == post.claimerID and not post.waitingApproval:
        post.waitingApproval = True
        db.session.commit()
        return jsonify({"message": "ReQuest finalised successfully!"}), 200
    return jsonify({"message": "Unable to finalise ReQuest."}), 400

@flaskApp.route('/relinquish_claim/<int:post_id>', methods=['POST'])
@login_required
def relinquish_claim(post_id):
    post = Posts.query.get(post_id)
    if post and post.claimed and current_user.userID == post.claimerID:
        post.claimed = False
        post.claimerID = None
        db.session.commit()
        return jsonify({"message": "Claim relinquished successfully!"}), 200
    return jsonify({"message": "Unable to relinquish claim."}), 400

@flaskApp.route('/approve_submission/<int:post_id>', methods=['POST'])
@login_required
def approve_submission(post_id):
    post = Posts.query.get(post_id)
    if post and post.waitingApproval and current_user.userID == post.posterID:
        post.completed = True
        post.waitingApproval = False
        db.session.commit()
        return jsonify({"message": "Submission approved successfully!"}), 200
    return jsonify({"message": "Unable to approve submission."}), 400

@flaskApp.route('/deny_submission/<int:post_id>', methods=['POST'])
@login_required
def deny_submission(post_id):
    post = Posts.query.get(post_id)
    if post and post.waitingApproval and current_user.userID == post.posterID:
        post.waitingApproval = False
        db.session.commit()
        return jsonify({"message": "Submission denied."}), 200
    return jsonify({"message": "Unable to deny submission."}), 400

@flaskApp.route('/cancel_request/<int:post_id>', methods=['POST'])
@login_required
def cancel_request(post_id):
    post = Posts.query.get(post_id)
    if post and current_user.userID == post.posterID:
        db.session.delete(post)
        db.session.commit()
        return jsonify({"message": "ReQuest cancelled successfully."}), 200
    return jsonify({"message": "Unable to cancel ReQuest."}), 400
