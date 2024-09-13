from flask import Flask

# Initialize Flask application instance
app = Flask(__name__)

# Load configuration from config.py if exists
app.config.from_pyfile('config.py', silent=True)

# Import views module to register routes
from .. import views
