import os
from dotenv import load_dotenv

load_dotenv()

basedir = os.path.abspath(os.path.dirname(__file__))

# Configuration class
class Config(object):
	SQLALCHEMY_DATABASE_URI =  os.getenv('DATABASE_URL') or 'sqlite:///../instance/database.db'
	SQLALCHEMY_TRACK_MODIFICATIONS = False
	SECRET_KEY = os.getenv("FLASK_SECRET_KEY")
	# Set local secret key with
	# BASH: echo 'export FLASK_SECRET_KEY="your_secret_key_here"' >> ~/.bashrc && source ~/.bashrc
	# WINDOWS CMD: set FLASK_SECRET_KEY=your_secret_key_here

	# with dotenv, you can instead create a .env file and set a local secret key in the same style as Windows

class DeploymentConfig(Config):
    SQLACHEMY_DATABASE_URI = "sqlite:///" +os.path.join(basedir,'test.db')
    
class TestConfig(Config):
    SQLACHEMY_DATABASE_URI = "sqlite:///:memory" 
    TESTING = True 