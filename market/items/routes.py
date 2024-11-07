import io
import os
import secrets
import shutil
from PIL import Image, ImageOps  # Importing necessary libraries for image processing
from flask import current_app
from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for
)
from market import db  # Import database object
from market.items.forms import PostForm  # Import the form for posting items
from market.models import Item, Picture  # Import models for item and picture

# Create a blueprint for item-related routes
items = Blueprint("items", __name__)

# Route to redirect to the market page without a category selection
@items.route("/categories", methods=["GET"])
def categories_redirect():
    return redirect(url_for("items.market_page"))
# Main route for displaying the market page with item filters and price sorting
@items.route("/market", methods=["GET"])
def market_page():
    post_form = PostForm()  # Initialize the PostForm for adding new items

    # Get filter parameters from the query string
    category = request.args.get("category")
    price_range = request.args.get("priceRange")
    location = request.args.get("location")
    delivery = request.args.get("delivery")
    sort_by_price = request.args.get("sort", 'asc')  # Get sorting choice (default to 'asc')

    # If no category is selected, render the default category view
    if not category:
        return render_template("market.html", type=None)

    # Base query filtered by the selected category
    query = Item.query.filter_by(type=category)

    # Apply price filtering based on selected price range
    if price_range:
        if price_range == "1":
            query = query.filter(Item.price < 50)
        elif price_range == "2":
            query = query.filter(Item.price.between(50, 100))
        elif price_range == "3":
            query = query.filter(Item.price > 100)

    # Apply location filtering based on the entered location
    if location:
        query = query.filter(Item.location.ilike(f"%{location}%"))

    # Apply delivery filtering if the option is selected
    if delivery:
        query = query.filter(Item.delivery == delivery)

    # Apply sorting by price (ascending or descending)
    if sort_by_price == 'asc':
        query = query.order_by(Item.price.asc())
    elif sort_by_price == 'desc':
        query = query.order_by(Item.price.desc())

    # Fetch all items matching the query filters and sorting
    market_items = query.all()

    # Render the market template with the filtered and sorted items and the form
    return render_template(
        "market.html", market_items=market_items, post_form=post_form, type=category
    )


# Function to save item pictures with resizing and compression
def add_item_picture(form_picture, item_name, item_id):
    # Generate a random hex for the picture file name
    random_hex = secrets.token_hex(8)
    _, f_extension = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_extension

    # Define the path to save the picture in the static/image_pics/item_id directory
    directory_path = os.path.join(
        current_app.root_path, "static", "image_pics", str(item_id)
    )

    # Create the directory if it doesn't exist
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)

    picture_path = os.path.join(directory_path, picture_fn)

    # Open the uploaded image file
    i = Image.open(form_picture)

    # Correct image orientation based on EXIF data
    i = ImageOps.exif_transpose(i)

    # Resize the image and maintain aspect ratio
    output_size = (800, 800)  # Resize to 800x800 pixels
    i.thumbnail(output_size)

    # Save the image with compression to reduce file size
    with io.BytesIO() as output:
        i.save(output, format="JPEG", quality=85)  # Save with 85% quality
        output.seek(0)
        i.save(picture_path, "JPEG")  # Save to the specified directory

    return picture_fn  # Return the generated picture filename


# Route to remove an image from the database and filesystem
@items.route("/remove_image/<int:image_id>", methods=["POST"])
def remove_image(image_id):
    # Fetch the image record from the database using its ID
    picture = Picture.query.get(image_id)

    if picture:
        # Get the image file name and directory path
        image_name = picture.image_name
        product_id = str(picture.product)
        directory_path = os.path.join(
            current_app.root_path, "static", "image_pics", product_id
        )
        file_path = os.path.join(directory_path, image_name)

        # Try to remove the file from the filesystem
        try:
            if os.path.exists(file_path):
                os.remove(file_path)  # Delete the file if it exists
                flash("File deleted successfully.", "success")
            else:
                flash(f"File does not exist: {file_path}", "warning")
        except Exception as e:
            flash(f"Error occurred while deleting file: {e}", "error")

        # Try to remove the image record from the database
        try:
            db.session.delete(picture)  # Delete the image record from the database
            db.session.commit()  # Commit the transaction
            flash("Image removed successfully!", "success")
        except Exception as e:
            flash(f"Error occurred while removing image from database: {e}", "error")
            db.session.rollback()  # Rollback transaction in case of error
    else:
        flash("Image not found!", "error")

    # Redirect back to the referring page or a default route
    return redirect(request.referrer or url_for("default_route"))


# Route to remove an item from the database and filesystem
@items.route("/remove_item/<int:item_id>", methods=["POST"])
def remove_item(item_id):
    # Fetch the item from the database using item_id
    product = Item.query.get(item_id)

    if product:
        try:
            # Define the path to the item's image directory
            directory_path = os.path.join(
                current_app.root_path, "static", "image_pics", str(item_id)
            )

            # Check if the directory exists and delete it
            if os.path.exists(directory_path):
                shutil.rmtree(directory_path)  # Remove the entire directory and its contents

            # Remove the item from the database
            db.session.delete(product)  # Delete the item from the database
            db.session.commit()  # Commit the transaction
            flash(f"Item successfully removed.", "success")

        except Exception as e:
            # Handle exceptions that occur during the removal process
            db.session.rollback()  # Rollback the transaction in case of error
            flash(f"An error occurred while removing the item: {str(e)}", "danger")

    else:
        flash("Item not found.", "warning")

    # Redirect back to the referring page or a default route
    return redirect(request.referrer or url_for("default_route"))
