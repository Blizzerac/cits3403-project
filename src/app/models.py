from app import app, db
from flask_login import UserMixin
from datetime import datetime

# Users table to handle logins
class Users(db.Model, UserMixin):
  userID = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(20), unique=True, nullable=False) # Usernames are unique
  email = db.Column(db.String(80), unique=True, nullable=False) # Emails are also unique
  password = db.Column(db.String(80), nullable=False)
  creationDate = db.Column(db.DateTime, nullable=False, default=datetime.now) # User account creation date

# Posts tables to handle each ReQuest
class Posts(db.Model):
  postID = db.Column(db.Integer, primary_key=True)
  posterID = db.Column(db.Integer, db.ForeignKey('users.userID'), nullable=False) # Quest submitter ID
  claimerID = db.Column(db.Integer, db.ForeignKey('users.userID'), nullable=False) # Quest accepter ID(s)?
  claimed = db.Column(db.Boolean, nullable=False, default=False) # If a quest is claimed currently
  completed = db.Column(db.Boolean, nullable=False, default=False) # If a quest is completed
  title = db.Column(db.Text, nullable=False) # Title of the quest
  description = db.Column(db.Text, nullable=False) # Description of the quest
  creationDate = db.Column(db.DateTime, nullable=False, default=datetime.now) # Post creation date
  claimDate = db.Column(db.DateTime, nullable=True) # Current claim's start date

# Each reponse to a certain ReQuest
class Responses(db.Model):
  postID = db.Column(db.Integer, db.ForeignKey('posts.postID'), nullable=False) # Quest ID
  responseID = db.Column(db.Integer, primary_key=True, nullable=False) # Unique ID of the response
  userID = db.Column(db.Integer, db.ForeignKey('users.userID'), nullable=False) # Responder ID
  response = db.Column(db.Text, nullable=False) # Response to the quest
  creationDate = db.Column(db.DateTime, nullable=False, default=datetime.now) # Response creation date

# Data base initialisation
def init_db():
  with app.app_context():
      db.create_all()