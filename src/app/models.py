from app import db
from flask_login import UserMixin
from datetime import datetime


class User(db.Model, UserMixin):
  userID = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(20), unique=True, nullable=False) # UNIQUE username
  password = db.Column(db.String(80), nullable=False)
  creationDate = db.Column(db.DateTime, nullable=False, default=datetime.utcnow) # User account creation date


# Run once
def init_db():
    with app.app_context():
        db.create_all()

def validate_username(username):
   existing_user = User.query.filter_by(username=username.data).first()

   if existing_user:
      return False
   return True