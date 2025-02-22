from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS

from app.config import Config
from app.routes import google_sheets_bp


def create_app():
    """
    Create and configure the Flask application.

    This function initializes the Flask application instance, configures it,
    and registers the necessary extensions and blueprints.

    Returns:
        Flask: The configured Flask application instance.
    """

    app = Flask(__name__)
    CORS(app)
    load_dotenv()
    app.config.from_object(Config)

    # Register extensions
    app.register_blueprint(google_sheets_bp)

    return app

# The create_app function initializes the Flask application instance,
# configures it, and registers the necessary extensions and blueprints.
