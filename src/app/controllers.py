# Imports
from flask import flash
from flask_login import login_required, login_user, logout_user, current_user
from app.models import Users, Posts, Responses, GoldChanges, PostChanges # Particular tables to be used
from app import models, forms
from app import db
from sqlalchemy import func, or_ , desc
from sqlalchemy.exc import SQLAlchemyError

# Errors to raise
class DatabaseError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class InvalidLogin(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class AccountAlreadyExists(Exception):
    def __init__(self, message):
        super().__init__(self.message)
        self.message = message

class InvalidAction(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class InvalidPermissions(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

def flash_db_error(debug, error, msg):
    # Ensure message is a string
    error = str(error)
    
    if debug:
        flash(f'Database error: {error}', 'danger')
    else: 
        flash(f'{msg} Please try again later or contact staff.', 'danger')
    
def try_signup_user(signup_form):
    try:
        existing_user = Users.query.filter_by(username=signup_form.username.data).first()
        existing_email = Users.query.filter_by(email=signup_form.email.data.lower()).first() # MUST lower email (case insensitive)
    except SQLAlchemyError as e:
        raise e

    # Check for existing users
    if existing_user:
        raise AccountAlreadyExists('Username is already taken.')
    if existing_email:
        raise AccountAlreadyExists('An account with this email already exists.')

    if not existing_user and not existing_email:
        new_user = Users(username=signup_form.username.data, email=signup_form.email.data.lower())
        new_user.set_password(signup_form.password.data)
        db.session.add(new_user)
        # Try commit new user to database.
        try:
            db.session.commit()
            login_user(new_user, remember=False) # Assuming dont remember them
            flash('Account created successfully!', 'success')
        # If failed, rollback database and warn user.
        except Exception as e:
            db.session.rollback()
            raise e
        
def try_login_user(login_form):
    user_input = login_form.login.data
    # Determine if the input is an email or username
    try:
        if "@" in user_input:
            user = Users.query.filter_by(email=user_input.lower()).first() # MUST lower email to remain case insensitive
        else:
            user = Users.query.filter_by(username=user_input).first()
    except SQLAlchemyError as e:
        raise e

    # Check password hash and login
    if user and user.check_password(login_form.password.data):
        login_user(user, remember=login_form.remember_me.data)
        flash('Logged in successfully!', 'success')
    else:
        raise InvalidLogin("Incorrect account details.")

def try_post_quest(posting_form):
    # Check if a user has enough gold & user's available gold
    if not current_user.quest_create(posting_form.post_reward.data):
        raise InvalidAction("Not enough gold to uphold the reward!")
    
    else:
        try:
            new_post = Posts(posterID=current_user.userID, title=posting_form.post_name.data, description=posting_form.post_description.data, reward=posting_form.post_reward.data)
            db.session.add(new_post)
            db.session.flush() # Push new post to database to assign its postID (used for logging)
            new_post.create_post_log(current_user.userID)
            db.session.commit()
    
        except Exception as e:
            db.session.rollback()
            raise e
        
def try_quest_view(request):
    # If no postID given, return user to the home screen
    post_id = request.args.get('postID') # Get the post ID to show
    if not post_id:
        raise InvalidAction('Incorrect usage.')
    
    # If no post exists, return user to home screen
    post = Posts.query.get(post_id)
    if not post:
        raise InvalidAction('ReQuest does not exist.')
    
    if post.private and not (current_user.userID == post.claimerID or current_user.userID == post.posterID):
        raise InvalidPermissions('Cannot acces private ReQuest.')
    
    if post.deleted and not current_user.isAdmin:
        raise InvalidPermissions('Cannot access cancelled ReQuest.')
    
    return post

def try_quest_respond(post, response_form):
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
        raise e
    
def try_search_quests(request, searching_form, quest_type):
    try:
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

        return posts
    
    except SQLAlchemyError as e:
        raise e
    
def try_redeem_gold(request):
    try:
        data = request.get_json()
        coinsToAdd = data['coins']
        current_user.add_gold(coinsToAdd)
        db.session.commit()
        flash('You earned ' + str(coinsToAdd) + 'G!', 'success')
    except Exception as e:
        db.session.rollback()
        raise e
    
def try_claim_quest(post_id):
    try:
        post = Posts.query.get(post_id)
    except SQLAlchemyError as e:
        raise e
    
    if not post:
        raise InvalidAction("No ReQuest wiht that ID.")
        
    # Check if a post is deleted -> Can't modify
    if post.deleted:
        raise InvalidAction("Cannot modify cancelled ReQuest.")

    if post and not post.claimed and current_user.userID != post.posterID:
        try:
            post.claim_post(current_user.userID)
            db.session.commit()
            return
        except Exception as e:
            db.session.rollback()
            raise e
        
    raise InvalidAction("Unable to claim ReQuest. Is it already claimed?")

def try_claim_quest(post_id):
    try:
        post = Posts.query.get(post_id)
    except SQLAlchemyError as e:
        raise e

    if not post:
        raise InvalidAction("No ReQuest with that ID.")
    if post.deleted:
        raise InvalidAction("Cannot modify cancelled ReQuest.")
    if post and not post.claimed and current_user.userID != post.posterID:
        try:
            post.claim_post(current_user.userID)
            db.session.commit()
            return
        except Exception as e:
            db.session.rollback()
            raise e
        
    raise InvalidAction("Unable to claim ReQuest. Is it already claimed?")

def try_finalise_quest(post_id):
    try:
        post = Posts.query.get(post_id)
    except SQLAlchemyError as e:
        raise e

    if not post:
        raise InvalidAction("No ReQuest with that ID.")
    if post.deleted:
        raise InvalidAction("Cannot modify cancelled ReQuest.")
    if post and post.claimed and current_user.userID == post.claimerID and not post.waitingApproval:
        try:
            post.finalise_submission(current_user.userID)
            db.session.commit()
            return
        except Exception as e:
            db.session.rollback()
            raise e
        
    raise InvalidAction("Unable to finalise ReQuest. Have you claimed it?")

def try_relinquish_claim(post_id):
    try:
        post = Posts.query.get(post_id)
    except SQLAlchemyError as e:
        raise e

    if not post:
        raise InvalidAction("No ReQuest with that ID.")
    if post.deleted:
        raise InvalidAction("Cannot modify cancelled ReQuest.")
    if post and post.claimed and current_user.userID == post.claimerID:
        try:
            post.unclaim_post(current_user.userID)
            db.session.commit()
            return
        except Exception as e:
            db.session.rollback()
            raise e
        
    raise InvalidAction("Unable to relinquish ReQuest claim. Have you claimed it?")

def try_approve_submission(post_id):
    try:
        post = Posts.query.get(post_id)
    except SQLAlchemyError as e:
        raise e

    if not post:
        raise InvalidAction("No ReQuest with that ID.")
    if post.deleted:
        raise InvalidAction("Cannot modify cancelled ReQuest.")
    if post and post.waitingApproval and current_user.userID == post.posterID:
        try:
            post.approve_submission(current_user.userID)
            gold = post.reward
            post.poster.quest_payout(gold)
            post.claimer.quest_completed(gold)
            db.session.commit()
            return
        except Exception as e:
            db.session.rollback()
            raise e
        
    raise InvalidAction("Unable to approve ReQuest submission. Has it been submitted for approval?")

def try_deny_submission(post_id):
    try:
        post = Posts.query.get(post_id)
    except SQLAlchemyError as e:
        raise e

    if not post:
        raise InvalidAction("No ReQuest with that ID.")
    if post.deleted:
        raise InvalidAction("Cannot modify cancelled ReQuest.")
    if post and post.waitingApproval and current_user.userID == post.posterID:
        try:
            post.deny_submission(current_user.userID)
            db.session.commit()
            return
        except Exception as e:
            db.session.rollback()
            raise e
        
    raise InvalidAction("Unable to deny ReQuest submission. Has it been submitted for approval?")

def try_private_request(post_id):
    try:
        post = Posts.query.get(post_id)
    except SQLAlchemyError as e:
        raise e

    if not post:
        raise InvalidAction("No ReQuest with that ID.")
    if post.deleted:
        raise InvalidAction("Cannot modify cancelled ReQuest.")
    if post and post.claimed and current_user.userID == post.posterID:
        try:
            post.private_post(current_user.userID)
            db.session.commit()
            return
        except Exception as e:
            db.session.rollback()
            raise e
        
    raise InvalidAction("Unable to change ReQuest privacy. Is it claimed?")

def try_cancel_request(post_id):
    try:
        post = Posts.query.get(post_id)
    except SQLAlchemyError as e:
        raise e

    if not post:
        raise InvalidAction("No ReQuest with that ID.")
    if post.deleted:
        raise InvalidAction("Cannot modify cancelled ReQuest.")
    if post and not post.completed and (current_user.userID == post.posterID or current_user.isAdmin):
        try:
            post.cancel_post(current_user.userID)
            gold = post.reward
            post.poster.quest_refund(gold)
            db.session.commit()
            return
        except Exception as e:
            db.session.rollback()
            raise e
        
    raise InvalidAction("Unable to cancel ReQuest. Do you own it?")