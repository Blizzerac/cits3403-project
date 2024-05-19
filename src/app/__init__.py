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
    db.init_app(flaskApp)
    login_manager.init_app(flaskApp)

    from app.models import Users
    @login_manager.user_loader
    def load_user(user_id):
        return Users.query.get(int(user_id))
    
    from app.blueprints import main
    flaskApp.register_blueprint(main)
                         
    return flaskApp

