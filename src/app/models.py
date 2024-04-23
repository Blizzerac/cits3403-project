from app import app, db
from flask_login import UserMixin
from datetime import datetime

class Users(db.Model, UserMixin):
  userID = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(20), unique=True, nullable=False) # Usernames are unique
  email = db.Column(db.String(80), unique=True, nullable=False) # Emails are also unique
  password = db.Column(db.String(80), nullable=False)
  creationDate = db.Column(db.DateTime, nullable=False, default=datetime.now()) # User account creation date

class Posts(db.Model):
  postID = db.Column(db.Integer, primary_key=True)
  posterID = db.Column(db.Integer, nullable=False) # Quest submitter ID
  claimerID = db.Column(db.Integer, nullable=False) # Quest accepter ID(s)?
  claimDate = db.Column(db.DateTime, nullable=False, default=datetime.now())
  brief = db.Column(db.Text, nullable=False) # Title of the quest
  content = db.Column(db.Text, nullable=False) # Description of the quest
  creationDate = db.Column(db.DateTime, nullable=False, default=datetime.now()) # User account creation date

class Responses(db.Model, UserMixin):
  responseID = db.Column(db.Integer, primary_key=True)
  postID = db.Column(db.Integer, nullable=False) # Quest ID
  userID = db.Column(db.Integer, primary_key=True) # Responder ID
  response = db.Column(db.Text, nullable=False) # Response to the quest
  creationDate = db.Column(db.DateTime, nullable=False, default=datetime.now()) # User account creation date


# Run once
def init_db():
    with app.app_context():
        db.create_all()