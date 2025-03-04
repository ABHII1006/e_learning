import sys
import os

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask
from .config import Config
from .routes import main_routes

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config.from_object(Config)

# Register routes
app.register_blueprint(main_routes)

if __name__ == '__main__':
    app.run(debug=True)
