# Imports
from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Login manager
login_manager = LoginManager()
login_manager.login_view = "login"

def create_app(config):
    # Main application name
    flaskApp = Flask(__name__, template_folder='../templates', static_folder='../static')

    # Configure flask app
    flaskApp.config.from_object(config)

    # Initialise using flask app
    from app.blueprints import main
    flaskApp.register_blueprint(main)
    db.init_app(flaskApp)
    login_manager.init_app(flaskApp)

    return flaskApp

# Import routes and models at the end to avoid circular imports
from app import routes, models

# Initialise database on startup (if it doesnt exist).
#models.init_db()

# User loader function
@login_manager.user_loader
def load_user(userID):
        return models.Users.query.get(int(userID))
