# Imports
from app import create_app, db
from app.config import TestConfig
from app import models
from app import models

# Main application code

# Create the Flask app
print("Creating app with testconfig")
flaskApp = create_app(TestConfig)
migrate = Migrate(flaskApp, db)
