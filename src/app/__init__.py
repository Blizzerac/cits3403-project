# Imports
from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from app.config import Config, TestConfig

db = SQLAlchemy()

def create_app(config):
    # Main application name
    flaskApp = Flask(__name__, template_folder='../templates', static_folder='../static')

    # Configuration
    #flaskApp = Flask(__name__)
    flaskApp.config.from_object(config)
    #flaskApp.debug = True # Debug error messages

    db.init_app(flaskApp)
   
    
    # Initialise extensions
    #db = SQLAlchemy(flaskApp)
    #migrate = Migrate(flaskApp, db)
    
    # Login manager
    login_manager = LoginManager()
    login_manager.init_app(flaskApp)
    login_manager.login_view = "login"

    # Import routes and models at the end to avoid circular imports
    from app import routes, models

    # Register blueprints
    from app.main_bp import main_bp
    flaskApp.register_blueprint(main_bp)

    # Initialise database on startup (if it doesnt exist).
    models.init_db()

    #User loader function
    @login_manager.user_loader
    def load_user(userID):
        return models.Users.query.get(int(userID))

    return flaskApp
