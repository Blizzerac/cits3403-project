from app import db
from flask_login import UserMixin
from datetime import datetime
from sqlalchemy import func, select
from sqlalchemy.ext.hybrid import hybrid_property
from werkzeug.security import generate_password_hash, check_password_hash


# Users table to handle logins
class Users(db.Model, UserMixin):
    userID = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False, index=True) # Usernames are unique
    email = db.Column(db.String(320), unique=True, nullable=False, index=True) # Emails are also unique (maximum determined from physical maximum researched)
    password = db.Column(db.String(128), nullable=False)
    isAdmin = db.Column(db.Boolean, nullable=False, default=False) # Set a user's account as admin (allowed logs)
    gold = db.Column(db.BigInteger, default=0, nullable=False) # User's currency
    gold_available = db.Column(db.BigInteger, default=0, nullable=False) # User's available currency to make a quest with
    creationDate = db.Column(db.DateTime, nullable=False, default=datetime.now) # User account creation date

    posts = db.relationship('Posts', backref='poster', lazy='dynamic', foreign_keys='Posts.posterID') # Link user to posts they made - backpopulates Posts as well
    claims = db.relationship('Posts', backref='claimer', lazy='dynamic', foreign_keys='Posts.claimerID') # Link user to posts they've claimed - backpopulates Posts as well
    responses = db.relationship('Responses', backref='responder', lazy='dynamic', foreign_keys='Responses.responderID') # Link user to responses theyve made - backpopulates Responses as well

    # Number of quests a user has posted
    @hybrid_property
    def questCount(self):
        return len(self.posts)
    
    # Number of quests a user has completed
    @hybrid_property
    def questsCompleted(self):
        return sum(1 for post in self.posts if (post.claimed) and (post.completed) and (post.claimerID == self.userID))
      
    @questsCompleted.expression
    def questsCompleted(cls): # For use at the class level
        return (select([func.count(Posts.postID)])
            .where((Posts.claimerID == cls.userID) & (Posts.claimed == True) & (Posts.completed == True))
            .label("quests_completed"))

    # Override flask's expected 'id' naming scheme
    def get_id(self):
        return str(self.userID)
    
    # Gold handling
    def quest_create(self, gold_cost):
        if self.gold_available >= gold_cost:
            self.gold_available -= gold_cost
            db.session.add(GoldChanges(userID=self.userID, changeAmount=-gold_cost, reason='Quest Creation'))
            return True
        return False
    
    def quest_refund(self, gold_cost):
        self.gold_available += gold_cost
        db.session.add(GoldChanges(userID=self.userID, changeAmount=gold_cost, reason='Quest Refund'))
    
    def quest_payout(self, gold_reward):
        self.gold -= gold_reward # No need to check if negative, as this is handled when creating a quest.
        db.session.add(GoldChanges(userID=self.userID, changeAmount=-gold_reward, reason='Quest Payout'))

    def quest_completed(self, gold_reward):
        self.gold += gold_reward
        self.gold_available += gold_reward
        db.session.add(GoldChanges(userID=self.userID, changeAmount=-gold_reward, reason='Quest Completed'))

    def add_gold(self, gold):
        if gold >= 0: # Ensure user can't spam gold generator
            self.gold += gold
            self.gold_available += gold
            db.session.add(GoldChanges(userID=self.userID, changeAmount=gold, reason='Gold Addition'))

    # Password handling
    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)
    
    # Console printing representation
    def __repr__(self) -> str:
        # Assume to keep email and hashed password hidden for security
        return f'<USER {self.username} ({self.userID}) - Created: {self.creationDate}>'

# Posts tables to handle each ReQuest
class Posts(db.Model):
    postID = db.Column(db.Integer, primary_key=True)
    posterID = db.Column(db.Integer, db.ForeignKey('users.userID'), nullable=False, index=True) # Quest submitter's ID
    claimerID = db.Column(db.Integer, db.ForeignKey('users.userID'), nullable=True, index=True) # Quest accepter's ID (can be null if not claimed)
    claimed = db.Column(db.Boolean, nullable=False, default=False) # If a quest is claimed currently
    waitingApproval = db.Column(db.Boolean, nullable=False, default=False) # If the user who claimed quest is waiting on approval from requester
    private = db.Column(db.Boolean, nullable=False, default=False) # If a quest can be viewed after claiming it
    completed = db.Column(db.Boolean, nullable=False, default=False) # If a quest is completed
    deleted = db.Column(db.Boolean, nullable=False, default=False) # If a quest is deleted by the poster (cant be accessed anymore, but still exists)
    title = db.Column(db.Text, nullable=False) # Title of the quest
    description = db.Column(db.Text, nullable=False) # Description of the quest
    reward = db.Column(db.BigInteger, nullable=False, default=0) # Reward for completing the quest
    creationDate = db.Column(db.DateTime, nullable=False, default=datetime.now) # Post creation date
    claimDate = db.Column(db.DateTime) # Current claim's start date

    responses = db.relationship('Responses', backref='post', lazy=True, cascade='all, delete-orphan', order_by='Responses.creationDate.asc()') # Link posts to their responses, sorted by creation date (ensure post deletion deletes responses)

    def create_post_log(self, userID):
        db.session.add(PostChanges(postID=self.postID, userID=userID, changeType='CREATED'))

    def claim_post(self, userID):
        if not self.claimed:
            self.claimed = True
            self.claimerID = userID
            self.claimDate = datetime.now()
            db.session.add(PostChanges(postID=self.postID, userID=userID, changeType='CLAIMED'))
    
    def finalise_submission(self, userID):
        if not self.waitingApproval:
            self.waitingApproval = True
            db.session.add(PostChanges(postID=self.postID, userID=userID, changeType='FINALISE_SUBMISSION'))
    
    def unclaim_post(self, userID):
        if self.claimed: # Further error checking handled before function
            self.claimed = False
            self.claimerID = None
            self.claimDate = None
            self.waitingApproval = False # Ensure to reset this (causes bug if not reset)
            self.private = False # Ensure others can take ReQuest
            db.session.add(PostChanges(postID=self.postID, userID=userID, changeType='UNCLAIMED'))
    
    def approve_submission(self, userID):
        if self.waitingApproval:
            self.waitingApproval = False
            self.completed = True
            db.session.add(PostChanges(postID=self.postID, userID=userID, changeType='APPROVED_SUBMISSION'))
    
    def deny_submission(self, userID):
        if self.waitingApproval:
            self.waitingApproval = False
            db.session.add(PostChanges(postID=self.postID, userID=userID, changeType='DENIED_SUBMISSION'))
    
    def private_post(self, userID):
        if self.private:
            self.private = False
            db.session.add(PostChanges(postID=self.postID, userID=userID, changeType='UNPRIVATED'))
        else:
            self.private = True
            db.session.add(PostChanges(postID=self.postID, userID=userID, changeType='PRIVATED'))
    
    def cancel_post(self, userID):
        if not self.deleted:
            self.deleted = True
            db.session.add(PostChanges(postID=self.postID, userID=userID, changeType='DELETED'))

# Each reponse to a certain ReQuest
class Responses(db.Model):
    responseID = db.Column(db.Integer, primary_key=True) # Unique ID of the response
    postID = db.Column(db.Integer, db.ForeignKey('posts.postID'), nullable=False, index=True) # Quest ID that this response is linked to
    responderID = db.Column(db.Integer, db.ForeignKey('users.userID'), nullable=False) # Responder ID
    msg = db.Column(db.Text, nullable=False) # Response to the quest
    creationDate = db.Column(db.DateTime, nullable=False, default=datetime.now) # Response creation date

# Changes to a user's gold
class GoldChanges(db.Model):
    changeID = db.Column(db.Integer, primary_key=True)
    userID = db.Column(db.Integer, db.ForeignKey('users.userID'), nullable=False, index=True) # userID of the user whos gold is modified
    changeAmount = db.Column(db.BigInteger, nullable=False)  # Positive for gain, negative for loss
    reason = db.Column(db.String(255), nullable=False)  # Reason for the change
    changeDate = db.Column(db.DateTime, nullable=False, default=datetime.now)

    user = db.relationship('Users', lazy='joined') # User information (not bidirectional)

    def __repr__(self):
        return f"<GOLD CHANGE ({self.changeID}):  {self.user.username} ({self.userID}) >> {self.changeAmount}G for '{self.reason}' [{self.changeDate}]>"

# Changes to a post (deletions, claiming, etc.)
class PostChanges(db.Model):
    changeID = db.Column(db.Integer, primary_key=True)
    postID = db.Column(db.Integer, db.ForeignKey('posts.postID'), nullable=False, index=True)
    userID = db.Column(db.Integer, db.ForeignKey('users.userID'), nullable=False, index=True)  # User who made the change
    changeType = db.Column(db.String(50), nullable=False)  # Type of change (Types: 'CREATED', 'CLAIMED', 'UNCLAIMED', 'FINALISE_SUBMISSION', 'DENIED_SUBMISSION', 'APPROVED_SUBMISSION', 'DELETED', 'PRIVATED', 'UNPRIVATED')
    changeDate = db.Column(db.DateTime, nullable=False, default=datetime.now)

    user = db.relationship('Users', lazy='joined') # User information (not bidirectional)
    post = db.relationship('Posts', lazy='joined') # Post information (not bidirectional)

    def __repr__(self):
        return f"<POST CHANGE ({self.changeID}):  {self.user.username} ({self.userID}) >> {self.changeType} on post {self.postID} [{self.changeDate}]>"


# # Data base initialisation
# def init_db():
#     with flaskApp.app_context():
#         db.create_all()

# def init_db_examples():
#     with flaskApp.app_context():
#         db.create_all()

#         # Insert example data
#         try:
#             new_admin = Users(username='admin', email='admin@example.com', isAdmin=True)
#             new_admin.set_password('Admin123')
#             db.session.add(new_admin)
#             new_user = Users(username='user', email='user@example.com')
#             new_user.set_password('User123')
#             db.session.add(new_user)
#             db.session.commit()
#         except Exception as e:
#             db.session.rollback()
#             print(f"Error adding example database entries. Error: {e}")