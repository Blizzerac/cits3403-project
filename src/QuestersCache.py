# Imports
from app import models
from app import create_app, db
from app.config import TestConfig, DeploymentConfig, Config
from flask_migrate import Migrate


flaskApp = create_app(TestConfig)
migrate = Migrate(flaskApp, db)

if __name__ == "__main__":
    flaskApp.run()