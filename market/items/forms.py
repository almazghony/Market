from flask_wtf import FlaskForm  # Import FlaskForm for creating forms
from flask_wtf.file import FileAllowed, FileField  # Import validators for file uploads
from wtforms import IntegerField, RadioField, StringField, SubmitField, TextAreaField  # Import fields for the form
from wtforms.validators import DataRequired, Length, NumberRange  # Import validators for form validation

# Form for removing an item
class RemoveForm(FlaskForm):
    submit = SubmitField(label="Remove")  # Submit button for removing an item


# Form for posting an item
class PostForm(FlaskForm):
    name = StringField(
        label="Name", 
        validators=[Length(max=30), DataRequired()]  # Name field with max length of 30 and required input
    )
    description = TextAreaField(
        label="Description", 
        validators=[Length(max=1500), DataRequired()]  # Description field with max length of 1500 and required input
    )
    location = StringField(
        label="Location", 
        validators=[Length(max=200), DataRequired()]  # Location field with max length of 200 and required input
    )
    price = IntegerField(
        label="Price",
        validators=[
            DataRequired(),  # Price field is required
            NumberRange(min=1, message="Price can't be zero")  # Validator to ensure price is greater than 0
        ],
    )
    type = RadioField(
        label="Category:", 
        choices=[("electronics", "Electronics"), ("clothes", "Clothes")],  # Radio field to select the category
        validators=[DataRequired()]  # Category selection is required
    )
    delivery = RadioField(
        label="Delivery:",
        choices=[("Yes", "Yes"), ("No", "No")],  # Radio field for selecting delivery option
        validators=[DataRequired()]  # Delivery option is required
    )
    picture = FileField(
        "Add Pictures", 
        validators=[FileAllowed(["jpeg", "png", "jpg"])]  # File upload field, allowing only jpeg, png, jpg formats
    )
    submit = SubmitField(label="Post Item")  # Submit button to post the item


# Form for updating an existing item
class UpdateItem(FlaskForm):
    name = StringField(
        label="Name", 
        validators=[Length(max=30), DataRequired()]  # Name field with max length of 30 and required input
    )
    description = TextAreaField(
        label="Description", 
        validators=[Length(max=1500), DataRequired()]  # Description field with max length of 1500 and required input
    )
    location = StringField(
        label="Location", 
        validators=[Length(max=200), DataRequired()]  # Location field with max length of 200 and required input
    )
    price = IntegerField(
        label="Price",
        validators=[
            DataRequired(),  # Price field is required
            NumberRange(min=1, message="Price can't be zero!")  # Validator to ensure price is greater than 0
        ],
    )
    type = RadioField(
        label="Category",
        choices=[("electronics", "Electronics"), ("clothes", "Clothes")],  # Radio field to select the category
        validators=[DataRequired()]  # Category selection is required
    )
    images = FileField(
        "Add Pictures", 
        validators=[FileAllowed(["jpeg", "png", "jpg"])]  # File upload field, allowing only jpeg, png, jpg formats
    )
    submit = SubmitField(label="Post Item")  # Submit button to post the updated item
