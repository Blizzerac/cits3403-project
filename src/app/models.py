from app import flaskApp, db
from flask_login import UserMixin
from datetime import datetime
from sqlalchemy import func, select
from sqlalchemy.ext.hybrid import hybrid_property
from werkzeug.security import generate_password_hash, check_password_hash


# Users table to handle logins
class Users(db.Model, UserMixin):
  userID = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(20), unique=True, nullable=False) # Usernames are unique
  email = db.Column(db.String(320), unique=True, nullable=False) # Emails are also unique (maximum determined from physical maximum researched)
  password = db.Column(db.String(80), nullable=False)
  gold = db.Column(db.BigInteger, default=0, nullable=False) # User's currency
  creationDate = db.Column(db.DateTime, nullable=False, default=datetime.now) # User account creation date

  posts = db.relationship('Posts', backref='poster', lazy='dynamic', foreign_keys='Posts.posterID') # Link user to posts they made
  claims = db.relationship('Posts', backref='claimer', lazy='dynamic', foreign_keys='Posts.claimerID') # Link user to posts they've claimed
  responses = db.relationship('Responses', backref='responder', lazy='dynamic', foreign_keys='Responses.responderID') # Link user to responses theyve made

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
  posterID = db.Column(db.Integer, db.ForeignKey('users.userID'), nullable=False) # Quest submitter ID
  claimerID = db.Column(db.Integer, db.ForeignKey('users.userID'), nullable=False) # Quest accepter ID(s)?
  claimed = db.Column(db.Boolean, nullable=False, default=False) # If a quest is claimed currently
  waitingApproval = db.Column(db.Boolean, nullable=False, default=False) # If the user who claimed quest is waiting on approval from requester
  private = db.Column(db.Boolean, nullable=False, default=False) # If a quest can be viewed after claiming it
  completed = db.Column(db.Boolean, nullable=False, default=False) # If a quest is completed
  title = db.Column(db.Text, nullable=False) # Title of the quest
  description = db.Column(db.Text, nullable=False) # Description of the quest
  reward = db.Column(db.BigInteger, nullable=False)
  creationDate = db.Column(db.DateTime, nullable=False, default=datetime.now) # Post creation date
  claimDate = db.Column(db.DateTime, nullable=True) # Current claim's start date

  responses = db.relationship('Responses', backref='post', lazy=True) # Link posts to their responses

# Each reponse to a certain ReQuest
class Responses(db.Model):
  postID = db.Column(db.Integer, db.ForeignKey('posts.postID'), nullable=False) # Quest ID
  responseID = db.Column(db.Integer, primary_key=True, nullable=False) # Unique ID of the response
  responderID = db.Column(db.Integer, db.ForeignKey('users.userID'), nullable=False) # Responder ID
  msg = db.Column(db.Text, nullable=False) # Response to the quest
  creationDate = db.Column(db.DateTime, nullable=False, default=datetime.now) # Response creation date

# Data base initialisation
def init_db():
  with flaskApp.app_context():
      db.create_all()