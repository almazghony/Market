import os

class Config:
    # Database URI - replace with your actual database URL
    SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI", "sqlite:///market.db")

    # Secret Key - make sure to set a strong, random secret key
    SECRET_KEY = os.environ.get("SECRET_KEY", "your_secret_key_here")

    # Password salt for hashing, ideally set a random value
    SECURITY_PASSWORD_SALT = os.environ.get("SECURITY_PASSWORD_SALT", "random_salt_value")

    # Email server configurations
    MAIL_SERVER = "smtp.gmail.com"  # Gmail’s SMTP server
    MAIL_PORT = 587  # Port for TLS
    MAIL_USE_TLS = True  # Enable TLS for email security
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME", "example@gmail.com")  # Your email address
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD", "your_email_password")  # App password for your email

    # Default sender info for emails
    MAIL_DEFAULT_SENDER = ("Your App Name", "yousefzmarket@gmail.com")

    # Security settings for cookies
    SESSION_COOKIE_SECURE = True  # HTTPS-only cookies
    SESSION_COOKIE_HTTPONLY = True  # Restrict cookies to HTTP(S) access only

    # Maximum upload size set to 16 MB
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB limit
