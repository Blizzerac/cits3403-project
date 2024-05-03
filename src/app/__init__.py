# Imports
from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from app.config import Config

# Main application name
app = Flask(__name__, template_folder='../templates', static_folder='../static')

# Configuration
app.config.from_object(Config)
app.debug = True

# Initialise extensions
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# Import routes and models at the end to avoid circular imports
from app import routes, models

# Initialise database on startup.
models.init_db()

# Login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(userID):
  return models.Users.query.get(int(userID))
