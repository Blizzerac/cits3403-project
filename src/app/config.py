import os

# Configuration class
class Config(object):
  SQLALCHEMY_DATABASE_URI =  os.environ.get('DATABASE_URL') or 'sqlite:///../instance/database.db'
  SQLALCHEMY_TRACK_MODIFICATION = False
  SECRET_KEY = 'placeholder' ### CHANGE THIS!
