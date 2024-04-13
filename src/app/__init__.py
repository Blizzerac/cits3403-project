# Imports
from flask import Flask

# Main application name
app = Flask(__name__, template_folder='../templates', static_folder='../static')

from app import routes