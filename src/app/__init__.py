# Imports
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

# Main application name
app = Flask(__name__, template_folder='../templates', static_folder='../static')

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../instance/database.db'  # Connects flask to databse
app.config['SECRET_KEY'] = 'placeholder'  ### CHANGE THIS!
app.debug = True

# Initialise extensions
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# Import routes and models at the end to avoid circular imports
from app import routes, models

# Initialise database on startup.
models.init_db()