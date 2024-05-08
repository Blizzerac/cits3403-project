import os

# Configuration class
class Config(object):
  SQLALCHEMY_DATABASE_URI =  os.environ.get('DATABASE_URL') or 'sqlite:///../instance/database.db'
  SQLALCHEMY_TRACK_MODIFICATIONS = False
  SECRET_KEY = os.environ.get("FLASK_SECRET_KEY")
  # Set local secret key with
  # BASH: echo 'export FLASK_SECRET_KEY="your_secret_key_here"' >> ~/.bashrc && source ~/.bashrc
  # WINDOWS CMD: set FLASK_SECRET_KEY=your_secret_key_here
