# Imports
from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from app.config import Config

# Main application name
flaskApp = Flask(__name__, template_folder='../templates', static_folder='../static')

# Configuration
flaskApp.config.from_object(Config)
flaskApp.debug = True

# Initialise extensions
db = SQLAlchemy(flaskApp)
migrate = Migrate(flaskApp, db)

# Login manager
login_manager = LoginManager()
login_manager.init_app(flaskApp)
login_manager.login_view = "login"

# Import routes and models at the end to avoid circular imports
from app import routes, models

# Initialise database on startup (if it doesnt exist).
models.init_db()

# User loader function
@login_manager.user_loader
def load_user(userID):
    return models.Users.query.get(int(userID))
