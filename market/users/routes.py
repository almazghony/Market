import os

from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_login import current_user, login_required, login_user, logout_user
from wtforms.validators import ValidationError

from market import db
from market.items.forms import PostForm, RemoveForm, UpdateItem
from market.items.routes import add_item_picture, remove_item
from market.models import Item, Picture, User
from market.users.forms import (
    ChangePasswordForm,
    LoginForm,
    RegisterForm,
    RemoveForm,
    ResetForm,
    UpdateForm,
)

# from market import cache
from market.users.utils import save_profile_picture, send_mail, send_verification_email

users = Blueprint("users", __name__)

# Limiter to restrict the number of requests from users to prevent abuse
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],  # Set rate limits globally
)


@users.route("/register", methods=["GET", "POST"])
@limiter.limit("10 per minute")  # Set rate limit specifically for the registration route
def register_page():
    form = RegisterForm()  # Initialize the registration form
    if form.validate_on_submit():
        # Store user data temporarily in the session
        session["new_user_data"] = {
            "name": form.name.data,
            "email_address": form.email_address.data,
            "mobile_number1": form.mobile_number1.data,
            "mobile_number2": form.mobile_number2.data,
            "password": form.password1.data,  # Store the plain password temporarily
        }

        # Send verification email to the user with the provided email address
        send_verification_email(form.email_address.data)

        flash("A verification email has been sent to your email address.", category="success")
        return redirect(url_for("users.resend_verification"))

    # Check and display form errors if any
    if form.errors:
        for error in form.errors.values():
            flash(error, category="danger")

    return render_template("register.html", form=form)  # Render the registration template


@users.route("/login", methods=["GET", "POST"])
@limiter.limit("10 per minute")  # Set rate limit specifically for the login route
def login_page():
    change_password_form = ChangePasswordForm()  # Initialize change password form
    reset_form = ResetForm()  # Initialize reset form
    form = LoginForm()  # Initialize login form

    if request.method == "POST":
        # Handle login form submission
        if "login" in request.form and form.validate_on_submit():
            user = User.query.filter_by(email_address=form.email_address.data).first()

            # Check if user exists
            if user is None:
                flash("This username is not registered.", category="danger")
                return redirect(url_for("users.login_page"))

            # Validate password for the user
            if user.check_password(form.password.data):
                login_user(user)
                flash(f"Success! Welcome {user.name}", category="success")
                return redirect(
                    url_for("items.categories_redirect")
                )  # Redirect to the categories page after successful login
            else:
                flash("Invalid password!", category="danger")
                return redirect(url_for("users.login_page"))

    # Handle GET request to render the login page
    return render_template(
        "login.html",
        form=form,
        change_password_form=change_password_form,
        reset_form=reset_form,
    )


@users.route("/logout")
def logout_page():
    # Logout the current user and display a message
    logout_user()
    flash("You have been logged out!", category="info")
    return redirect(url_for("items.categories_redirect"))  # Redirect to categories page


@users.route("/account", methods=["POST", "GET"])
@login_required  # Ensure the user is logged in before accessing the account page
# @cache.cached(timeout=300)
def profile_page():
    post_form = PostForm()  # Initialize post form for posting new items
    remove_form = RemoveForm()  # Initialize remove form for deleting items
    update_form = UpdateForm(  # Pre-populate user details in the update form
        name=current_user.name,
        email_address=current_user.email_address,
        mobile_number1=current_user.mobile_number1,
        mobile_number2=current_user.mobile_number2,
        state=current_user.state,
    )

    update_item = UpdateItem()  # Form for updating item details
    owned_items = Item.query.filter_by(owner=current_user.id)  # Get all items owned by the current user

    if request.method == "POST":
        # Handle item removal process
        if "removed_item" in request.form and remove_form.validate_on_submit():
            removed_item = request.form.get("removed_item")
            item_obj = Item.query.filter_by(id=removed_item).first()
            if item_obj:
                if current_user.can_remove(item_obj):
                    item_obj.remove()  # Remove the item from the database
                    flash("تم حذف العنصر بنجاح", category="success")
                else:
                    flash("يمكن لصاحب العنصر فقط حذفه", category="danger")
            else:
                flash("لم يتم العثور على العنصر", category="danger")
            return redirect(
                url_for("users.profile_page")
            )  # Redirect back to the profile page after removing the item

        # Handle item posting process
        if "posted_item" in request.form and post_form.validate_on_submit():

            if post_form.errors:  # Check for form validation errors
                for error in post_form.errors.values():
                    print(f"{error}", category="danger")
            else:
                # Create a new item with the posted details
                new_item = Item(
                    name=post_form.name.data,
                    price=post_form.price.data,
                    location=post_form.location.data,
                    description=post_form.description.data,
                    type=post_form.type.data,
                    delivery=post_form.delivery.data,
                    owner=current_user.id,  # Set the current user as the owner
                )
                db.session.add(new_item)  # Add the new item to the database
                db.session.commit()
                flash("تم اضافة العنصر بنجاح", category="success")
                try:
                    # Handle file uploads for item pictures
                    files = request.files.getlist("picture")
                    for file in files:
                        image_name = add_item_picture(file, new_item.name, new_item.id)
                        new_pic = Picture(image_name=image_name, product=new_item.id)
                        db.session.add(new_pic)
                        db.session.commit()  # Commit new picture to the database
                except Exception as e:
                    print(f"Error saving picture {e}")

            return redirect(
                url_for("users.profile_page")
            )  # Redirect back to profile page after posting an item

        # Handle user profile update process
        if "updated_user" in request.form and update_form.validate_on_submit():
            if update_form.picture.data:  # Check if a new profile picture is uploaded
                if current_user.image_file:  # If the user has an existing profile picture
                    user_image = current_user.image_file
                    image_path = os.path.join(
                        current_app.root_path, "static", "profile_pics", user_image
                    )
                try:
                    # Remove the old profile picture from the file system
                    if os.path.exists(image_path):
                        os.remove(image_path)
                        print("File deleted successfully.")
                except Exception as e:
                    print(f"Error: {e}")

                # Save the new profile picture
                picture_file = save_profile_picture(update_form.picture.data)
                current_user.image_file = picture_file
            try:
                # Update user information in the database
                current_user.update_info(update_form)
                db.session.commit()  # Commit the updates to the database
                flash("تم تحديث البيانات بنجاح", category="success")
                return redirect(
                    url_for("users.profile_page")
                )  # Redirect back to the profile page after updating
            except ValidationError as e:
                flash(str(e), category="danger")  # Show specific validation errors
            except Exception as e:
                print(f"Unknown Error occurred: {str(e)}")

        # Handle item update process
        if "updated_item" in request.form and update_item.validate_on_submit():
            try:
                # Retrieve the current item from the form data
                current_item = request.form.get("updated_item")
                item_obj = Item.query.get(current_item)

                # Update item details with the new data
                item_obj.update_info(update_item)

                # Commit the updates to the database
                db.session.commit()
                flash("تم تحديث البيانات بنجاح", category="success")

                # Handle file uploads for images associated with the item
                files = request.files.getlist("images")
                if files:  # Ensure that files are present
                    for file in files:
                        # Save the new image and associate it with the item
                        image_name = add_item_picture(file, item_obj.name, item_obj.id)
                        new_pic = Picture(image_name=image_name, product=item_obj.id)
                        db.session.add(new_pic)

                    # Commit the images to the database
                    db.session.commit()
                else:
                    flash("No images were uploaded.", category="warning")

                # Redirect to the profile page after the update
                return redirect(url_for("users.profile_page"))

            except ValidationError as e:
                # Catch form validation errors and display them
                flash(str(e), category="danger")
            except Exception as e:
                # Catch any other errors and display them
                print(f"Unknown Error occurred: {str(e)}")

    # Handle GET requests to render the account page
    return render_template(
        "account.html",
        owned_items=owned_items,  # Pass the user's owned items to the template
        post_form=post_form,  # Pass the post form to the template
        remove_form=remove_form,  # Pass the remove form to the template
        update_form=update_form,  # Pass the update form to the template
        update_item=update_item,  # Pass the update item form to the template
    )









































@users.route("/owner/<int:owner_id>", methods=["POST", "GET"])
def owner_profile(owner_id):
    owner = User.query.get(owner_id)  # Fetch the owner user by ID
    remove_form = RemoveForm()  # Initialize the form for removing an item
    update_item = UpdateItem()  # Initialize the form for updating an item

    if request.method == "POST":
        # Check if the update item form has been submitted
        if "updated_item" in request.form and update_item.validate_on_submit():
            try:
                # Retrieve the current item ID from the form
                current_item_id = request.form.get("updated_item")
                item_obj = Item.query.get(current_item_id)  # Fetch the item by ID

                if item_obj is None:
                    flash("Item not found.", category="danger")
                    return redirect(url_for("users.owner_profile", owner_id=owner_id))

                # Update item details with the form data
                item_obj.update_info(update_item)

                # Handle file uploads for images
                files = request.files.getlist("images")
                if files:  # Ensure that files are present
                    for file in files:
                        # Save the new image and associate it with the item
                        image_name = add_item_picture(file, item_obj.name, item_obj.id)
                        new_pic = Picture(image_name=image_name, product=item_obj.id)
                        db.session.add(new_pic)

                # Commit the update to the database
                db.session.commit()
                flash("تم تحديث البيانات بنجاح", category="success")
            except ValidationError as e:
                # Catch form validation errors
                flash(str(e), category="danger")
            except Exception as e:
                # Catch any other errors and flash them
                print(f"Unknown error occurred: {str(e)}")

            # Redirect to the profile page after the update
            return redirect(url_for("users.owner_profile", owner_id=owner_id))

    # For GET requests, render the owner profile page
    return render_template(
        "owner.html", update_item=update_item, remove_form=remove_form, owner=owner
    )


@users.route("/verify_email/<token>")
def verify_email(token):
    email = User.verify_email_token(token)  # Verify the email token
    if not email:
        flash("The verification link is invalid or has expired.", category="danger")
        session.pop("new_user_data", None)  # Clear the session
        return redirect(url_for("users.register_page"))

    # Ensure the session has the correct user data
    if "new_user_data" not in session or session["new_user_data"]["email_address"] != email:
        flash("Something went wrong. Please register again.", category="danger")
        session.pop("new_user_data", None)  # Clear the session
        return redirect(url_for("users.register_page"))

    # Create the user now that the email is verified
    new_user_data = session.pop("new_user_data")  # Remove the data from session after use
    new_user = User(
        name=new_user_data["name"],
        email_address=new_user_data["email_address"],
        mobile_number1=new_user_data["mobile_number1"],
        mobile_number2=new_user_data["mobile_number2"],
        password=new_user_data["password"],  # Password is stored in session temporarily
        is_verified=True,  # Set user as verified
    )

    db.session.add(new_user)  # Add new user to the database
    db.session.commit()

    flash("Email verified successfully! You can now log in.", category="success")
    return redirect(url_for("users.login_page"))


@users.route("/reset_password", methods=["GET", "POST"])
def reset_password():
    reset_form = ResetForm()  # Initialize the password reset form
    if reset_form.validate_on_submit():
        user = User.query.filter_by(email_address=reset_form.email_address.data).first()
        if user:
            send_mail(user)  # Send the reset email
            flash("Check your email for a password reset link!", category="success")
            return redirect(url_for("users.login_page"))
        else:
            flash("Email does not exist.", category="danger")
            return redirect(url_for("users.login_page"))  # Redirect after error

    for error in reset_form.errors.values():
        print(error)
        flash(error)

    # Redirect to login page as reset password form is within a modal
    return redirect(url_for("users.login_page"))


@users.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_token(token):
    user = User.verify_token(token)  # Verify the token to retrieve the user
    if not user:
        flash("That is an invalid or expired token. Please try again.", "danger")
        return redirect(url_for("users.login_page"))

    change_password_form = ChangePasswordForm()  # Initialize the change password form
    if change_password_form.validate_on_submit():
        user.password = change_password_form.new_password.data  # Set the new password
        user.reset_token = None  # Clear the reset token after changing the password
        user.reset_token_expiration = None  # Clear expiration
        db.session.commit()
        flash("Your password has been updated! Please log in.", "success")
        return redirect(url_for("users.login_page"))  # Redirect to login after success

    return render_template("change_password.html", change_password_form=change_password_form)


@users.route("/remove_user/<int:user_id>", methods=["POST"])
def remove_user(user_id):
    user = User.query.get(user_id)  # Fetch the user by ID

    if user:
        # Remove profile picture if it exists
        if user.image_file:
            user_image = user.image_file
            image_path = os.path.join(
                current_app.root_path, "static", "profile_pics", user_image
            )
            try:
                if os.path.exists(image_path):
                    os.remove(image_path)  # Remove image from the file system
                    print("File deleted successfully.")
            except Exception as e:
                print(f"Error: {e}")

        # Remove user's items if they have any
        if user.items:
            for item in user.items:
                try:
                    item_id = int(item.id)
                    remove_item(item_id)  # Remove each item
                except Exception as e:
                    print(f"Error removing item with ID {item.id}: {e}")
        user.remove()  # Remove the user from the database
        flash(f" User successfully removed.", "success")

    return redirect(url_for("users.register_page"))  # Redirect to the register page


@users.route("/resend_verification", methods=["GET", "POST"])
def resend_verification():
    # Get the email from the session
    new_user_data = session.get("new_user_data")
    if new_user_data:
        email = new_user_data["email_address"]
        user = User.query.filter_by(email_address=email).first()
        if user:
            if user.is_verified:
                flash("User already verified.", category="danger")
            else:
                send_verification_email(email)  # Resend verification email
                flash("A new verification email has been sent!", category="success")
    else:
        flash("No pending registration found.", category="danger")

    return render_template("verification.html")  # Render the verification page
