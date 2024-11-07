import io
import os
import secrets
from PIL import Image, ExifTags  # Import Image for image handling, ExifTags for image metadata
from flask import current_app, flash, url_for  # Import necessary Flask modules
from flask_mail import Message  # Import for sending emails
from market import mail  # Import mail instance from the market module
from market.models import User  # Import User model for generating tokens


# Function to send password reset email
def send_mail(user):
    token = user.get_token()  # Assuming you have a get_token method in your User model to generate a token
    msg = Message(
        "Password Reset Request",  # Subject of the email
        recipients=[user.email_address],  # Recipient email address
        sender="yousefzmarket@gmail.com",  # Sender email address
    )

    # HTML formatted email body
    msg.html = f"""
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: #f8f9fa;
                color: #343a40;
                padding: 20px;
                border-radius: 5px;
                border: 1px solid #dee2e6;
            }}
            h2 {{
                color: #ff0000; /* Red color for headings */
            }}
            p {{
                font-size: 16px;
                line-height: 1.5;
            }}
            a {{
                color: #ff0000; /* Red color for links */
                text-decoration: none;
                font-weight: bold;
            }}
            a:hover {{
                text-decoration: underline;
            }}
            .footer {{
                margin-top: 20px;
                font-size: 12px;
                color: #6c757d;
            }}
        </style>
    </head>
    <body>
        <h2>Password Reset Request</h2>
        <p>
            To reset your password, please click the following link:
        </p>
        <p>
            <a href="{url_for('users.reset_token', token=token, _external=True)}">
                Reset Your Password
            </a>
        </p>
        <p>
            If you did not make this request, please ignore this email.
        </p>
        <div class="footer">
            <p>&copy; '2024' Flask Market. All Rights Reserved.</p>
        </div>
    </body>
    </html>
    """

    mail.send(msg)  # Send the email


# Function to save the profile picture
def save_profile_picture(form_picture):
    try:
        # Generate a random hex for the picture filename
        random_hex = secrets.token_hex(8)
        _, f_extension = os.path.splitext(form_picture.filename)  # Get the file extension
        picture_fn = random_hex + f_extension  # Create the picture filename
        picture_path = os.path.join(
            current_app.root_path, "static", "profile_pics", picture_fn
        )  # Set the file path to save the picture

        # Open the image using PIL
        i = Image.open(form_picture)

        # Handle image orientation using EXIF data to correct rotation
        try:
            for orientation in ExifTags.TAGS.keys():
                if ExifTags.TAGS[orientation] == "Orientation":
                    break
            exif = i._getexif()  # Get EXIF data from the image

            # Check and adjust image orientation if needed
            if exif is not None and orientation in exif:
                if exif[orientation] == 3:
                    i = i.rotate(180, expand=True)
                elif exif[orientation] == 6:
                    i = i.rotate(270, expand=True)
                elif exif[orientation] == 8:
                    i = i.rotate(90, expand=True)
        except Exception as e:
            print(f"Could not process EXIF data: {e}")

        # Resize the image to a smaller size for the profile picture
        output_size = (500, 500)
        i.thumbnail(output_size)

        # Save the image with compression to reduce file size
        with io.BytesIO() as output:
            i.save(
                output, format="JPEG", quality=85  # Save with 85% quality for compression
            )
            output.seek(0)  # Move the file pointer back to the beginning
            i.save(picture_path, "JPEG")  # Save the image to the file system

        return picture_fn  # Return the filename of the saved picture
    except Exception as e:
        print(f"Error saving profile picture: {e}")
        return None  # Return None if an error occurs


# Function to send verification email
def send_verification_email(email):

    token = User.generate_verification_token(email)  # Generate a token for email verification
    verification_link = url_for("users.verify_email", token=token, _external=True)  # Create verification URL

    msg = Message(
        "Verify Your Email",  # Subject of the email
        recipients=[email],  # Recipient email address
        sender="yousefzmarket@gmail.com",  # Sender email address
    )

    # HTML formatted email body for verification
    msg.html = f"""
    <html>
        <body style="font-family: Arial, sans-serif; color: #212121;">
            <h2 style="color: #212121;">Verify Your Email</h2>
            <p>To verify your email, please click the following link:</p>
            <p>
                <a href="{verification_link}" style="color: #0066cc; text-decoration: none; font-weight: bold;">
                    Verify Email
                </a>
            </p>
            <p>If you did not register, please ignore this email.</p>
            <p>Thank you!</p>
        </body>
    </html>
    """

    try:
        mail.send(msg)  # Try sending the verification email
    except Exception as e:
        flash(f"Failed to send email: {e}", "danger")  # Flash error message if sending fails
