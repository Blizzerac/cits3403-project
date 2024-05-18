# Imports
from app import create_app
from app.config import TestConfig, DeploymentConfig
from app import models
from app import models

# Main application code

# Create the Flask app
app = create_app(TestConfig)

# Main application code
if __name__ == "__main__":
    # Add any additional setup or initialization code here
    # For example, you might want to initialize the database
    # models.init_db()

    # Run the Flask app
    app.run()