# Imports
from app import models
from app import create_app, db
from app.config import DeploymentConfig

# Main application code
flaskApp = create_app(DeploymentConfig)
migrate = Migrate(db, flaskApp)