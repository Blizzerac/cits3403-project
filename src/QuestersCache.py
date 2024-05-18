# Imports
from app import create_app, db, login_manager
from app.config import TestConfig, DeploymentConfig, Config
from flask_migrate import Migrate
from app.models import Users


flaskApp = create_app(DeploymentConfig)
migrate = Migrate(flaskApp, db) # Comment this out when doing unit tests
