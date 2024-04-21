# Imports
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Main application name
app = Flask(__name__, template_folder='../templates', static_folder='../static')

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../instance/database.db'  # Connects flask to databse
app.config['SECRET_KEY'] = 'placeholder'  ### CHANGE THIS!

# Initialise SQLAlchemy
db = SQLAlchemy(app)

from app import routes, models