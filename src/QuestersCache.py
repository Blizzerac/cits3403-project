# Imports
from app import create_app, db, login_manager
from app.config import TestConfig, DeploymentConfig
from flask_migrate import Migrate

# Deployment Configuration
# flaskApp = create_app(DeploymentConfig)
# migrate = Migrate(flaskApp, db)

# Testing Configuration
flaskApp = create_app(TestConfig)

# Ensure db is created
with flaskApp.app_context():
    db.create_all()