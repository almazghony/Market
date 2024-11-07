from flask import Flask
from flask_bcrypt import Bcrypt
from flask_caching import Cache
from flask_login import LoginManager
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy

from market.config import Config

# Initialize extensions
mail = Mail()  # For sending emails
db = SQLAlchemy()  # For database interactions
bcrypt = Bcrypt()  # For password hashing

# Set up login manager for user authentication
login_manager = LoginManager()
login_manager.login_view = "users.login_page"  # Redirect to login page if not logged in
login_manager.login_message_category = "info"  # Message category for login alerts
login_manager.login_message = "Please Log in first"  # Message displayed when login is required


def create_app(config_class=Config):
    app = Flask(__name__)  # Create Flask application instance
    app.config.from_object(config_class)  # Load configuration from the specified class

    app.app_context().push()  # Push application context

    # Initialize extensions with the app
    mail.init_app(app)
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    # Optional caching setup (commented out)
    # cache = Cache(app, config={
    #     'CACHE_TYPE': 'SimpleCache',  # Cache type (e.g., 'RedisCache', 'FileSystemCache')
    #     'CACHE_DEFAULT_TIMEOUT': 300  # Default cache timeout in seconds
    # })
    # cache.init_app(app)

    # Import and register blueprints for different parts of the application
    from market.errors.handlers import errors
    from market.items.routes import items
    from market.main.routes import main
    from market.users.routes import users

    app.register_blueprint(users)  # User-related routes
    app.register_blueprint(items)  # Item-related routes
    app.register_blueprint(main)  # Main application routes
    app.register_blueprint(errors)  # Error handling routes

    return app  # Return the configured app instance
