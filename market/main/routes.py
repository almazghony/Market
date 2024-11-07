from flask import Blueprint, render_template

# Create a new Blueprint for organizing the main routes of the application
main = Blueprint("main", __name__)

# Importing the Limiter class to apply rate limiting for requests
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Initialize Limiter to limit the rate of requests based on the remote address (IP of the client)
limiter = Limiter(
    key_func=get_remote_address,  # This will use the client's IP address for limiting
    default_limits=["200 per day", "50 per hour"],  # Global rate limits (200 requests per day, 50 per hour)
)

# Route for the homepage, this is accessible via '/' or '/home' URLs
@main.route("/")
@main.route("/home")
# Apply rate limiting: Max 100 requests per minute for this route
@limiter.limit("100 per minute")
def home_page():
    # Render the 'home.html' template when a user visits the home page
    return render_template("home.html")


# Route for the about page, accessible via '/about' URL
@main.route("/about")
def about_page():
    # Render the 'about.html' template with a custom title passed to the template
    return render_template("about.html", title="About Us")
