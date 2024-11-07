from flask import current_app
from flask_login import UserMixin
from itsdangerous import URLSafeTimedSerializer as Serializer

from market import bcrypt, db, login_manager


# Load user by ID for session management
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer(), primary_key=True)  # User ID
    name = db.Column(db.String(length=30), nullable=False)  # User's name
    email_address = db.Column(db.String(length=64), nullable=False, unique=True)  # Unique email
    password_hash = db.Column(db.String(), nullable=False)  # Hashed password
    mobile_number1 = db.Column(db.String(11), nullable=False)  # Primary mobile number
    mobile_number2 = db.Column(db.String(11))  # Optional secondary mobile number
    image_file = db.Column(db.String(20))  # Profile image filename
    state = db.Column(db.String(), default="Didn'y write anything yet")  # User status message
    items = db.relationship("Item", backref="owned_user", lazy=True)  # Relationship to items owned
    is_verified = db.Column(db.Boolean, default=False)  # Email verification status

    @staticmethod
    def generate_verification_token(email):
        # Generate token for email verification
        serial = Serializer(current_app.config["SECRET_KEY"])
        return serial.dumps(
            {"email": email}, salt=current_app.config["SECURITY_PASSWORD_SALT"]
        )

    @staticmethod
    def verify_email_token(token, expires_sec=3600):
        # Verify the email token for validity
        serial = Serializer(current_app.config["SECRET_KEY"])
        try:
            email = serial.loads(
                token,
                salt=current_app.config["SECURITY_PASSWORD_SALT"],
                max_age=expires_sec,
            )["email"]
        except Exception as e:
            print("THE ERROR IS ", e)
            return None
        return email

    def get_token(self):
        # Create a token for user identification
        serial = Serializer(current_app.config["SECRET_KEY"])
        return serial.dumps(
            {"user_id": self.id}, salt=current_app.config["SECURITY_PASSWORD_SALT"]
        )

    @staticmethod
    def verify_token(token, expires_sec=300):
        # Verify the token to retrieve user ID
        serial = Serializer(current_app.config["SECRET_KEY"])
        try:
            user_id = serial.loads(
                token,
                salt=current_app.config["SECURITY_PASSWORD_SALT"],
                max_age=expires_sec,
            )["user_id"]
        except Exception as e:
            print("THE ERROR IS ", e)
            return None
        return User.query.get(user_id)

    @property
    def password(self):
        return self.password_hash  # Return the hashed password

    @password.setter
    def password(self, plain_text_password):
        # Set and hash the password
        self.password_hash = bcrypt.generate_password_hash(plain_text_password).decode(
            "utf-8"
        )

    def check_password(self, attempt_password):
        # Verify the provided password against the stored hash
        return bcrypt.check_password_hash(self.password, attempt_password)

    def can_remove(self, item_obj):
        # Check if the user can remove the item
        return item_obj in self.items

    def update_info(self, update_form):
        # Update user information from a form
        self.name = update_form.name.data
        self.email_address = update_form.email_address.data
        self.mobile_number1 = update_form.mobile_number1.data
        self.mobile_number2 = update_form.mobile_number2.data
        self.state = update_form.state.data
        db.session.commit()  # Commit changes to the database

    def remove(self):
        # Remove the user from the database
        db.session.delete(self)
        db.session.commit()


class Item(db.Model):
    id = db.Column(db.Integer(), primary_key=True)  # Item ID
    name = db.Column(db.String(length=30), nullable=False)  # Item name
    price = db.Column(db.Integer(), nullable=False)  # Item price
    type = db.Column(db.String(length=12), nullable=False)  # Item type
    description = db.Column(db.String(length=1024), nullable=False)  # Item description
    location = db.Column(db.String(), nullable=False)  # Item location
    delivery = db.Column(db.String(), nullable=False)  # Delivery method
    owner = db.Column(db.Integer(), db.ForeignKey("user.id"))  # Owner reference
    images = db.relationship("Picture", backref="rel_item", lazy=True)  # Related images

    def __repr__(self):
        return self.id  # Represent item by its ID

    def buy(self, current_user):
        # Transfer ownership of the item to the buyer
        self.owner = current_user.id
        current_user.budget -= self.price  # Deduct price from buyer's budget
        db.session.commit()  # Commit changes to the database

    def remove(self):
        # Remove the item from the database
        db.session.delete(self)
        db.session.commit()

    def update_info(self, update_form):
        # Update item information from a form
        self.name = update_form.name.data
        self.price = update_form.price.data
        self.type = update_form.type.data
        self.description = update_form.description.data
        self.location = update_form.location.data
        db.session.commit()  # Commit changes to the database


class Picture(db.Model):
    id = db.Column(db.Integer(), primary_key=True)  # Picture ID
    image_name = db.Column(db.String())  # Image filename
    product = db.Column(db.Integer(), db.ForeignKey("item.id"))  # Related item reference
