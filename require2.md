
---

# Digital Marketplace Web Application Documentation

This documentation provides a comprehensive guide for users of the **Digital Marketplace Web Application**. This platform is designed to facilitate the buying and selling of items across various categories, built using the **Flask** micro web framework.

---

## Table of Contents
1. [Overview](#overview)
2. [Features](#features)
3. [Technology Stack](#technology-stack)
4. [Installation](#installation)
5. [Usage](#usage)
6. [Folder Structure](#folder-structure)
7. [Marketplace Overview](#marketplace-overview)
8. [Authentication and Security](#authentication-and-security)
9. [Email Integration](#email-integration)
10. [Frontend and Styling](#frontend-and-styling)
11. [Deployment](#deployment)
12. [Support](#support)

---

## Overview

The **Digital Marketplace** offers a clean and intuitive interface where users can browse, list, and purchase items. The platform includes core e-commerce functionalities such as item listings, advanced search filters, and secure user account management. The application utilizes **Flask** as the backend framework, integrates email verification, password management, and profile customization. **Flask-Mail** handles email notifications, while **Bootstrap** ensures the user interface is responsive and visually appealing.

---

## Features

### 1. **User Registration and Authentication**
- **Flask-Login Integration**: Secure session management for user authentication.
- **Email Verification with Flask-Mail**: Users receive a verification link to activate their accounts.
- **Password Reset**: Secure password reset functionality using **Flask-Mail** and token-based authentication.
- **Flask-Bcrypt**: Securely hashes user passwords.
- **Form Validation with Flask-WTF**: Provides form handling and validation for a smooth user experience.

### 2. **User Profiles**
- **Profile Management**: Users can update personal details such as username, email, and profile picture.
- **Item Management**: Users can add, edit, and remove items from the marketplace.

### 3. **Marketplace Functionality**
- **Item Listings**: Items are categorized, including **Electronics** and **Clothing**.
- **Filtering Options**: Users can filter items by category, price, location, and delivery options.
- **Sorting**: Users can sort items by price.
- **User-friendly Interface**: The marketplace is designed for easy navigation with a responsive grid layout.

### 4. **Security Features**
- **Session Protection**: Implemented using **Flask-Login**.
- **Flask-Limiter**: Rate limiting to prevent abuse of specific endpoints.
- **CSRF Protection**: All forms are protected using **CSRF tokens**.
- **Form Validation**: Ensures secure form handling with **Flask-WTF**.
- **SQL Injection Protection**: Managed securely through **SQLAlchemy** ORM.

---

## Technology Stack

- **Backend**: Flask (Python)
  - **Flask-Bcrypt**: For secure password hashing.
  - **Flask-SQLAlchemy**: ORM for database management.
  - **Flask-Limiter**: Rate limiting to prevent abuse.
  - **Flask-Mail**: For handling email functionality.
  - **Flask-Login**: User session management.
  - **Flask-WTF**: Secure form handling with CSRF protection.
- **Frontend**: HTML5, CSS3, **Bootstrap** for responsive design, and **JavaScript**.
- **Database**: 
  - **SQLite** (development)
- **Email Service**: **Flask-Mail** for account verification and password resets.

---

## Installation

To install and run the application locally, follow these steps:

### 1. Clone the repository:
```bash
git clone https://github.com/almazghony/digital-marketplace.git
```

### 2. Navigate into the project directory:
```bash
cd digital-marketplace
```

### 3. Set up a virtual environment:
- On **Linux/MacOS**:
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```
- On **Windows**:
  ```bash
  python -m venv venv
  venv\Scripts\activate
  ```

### 4. Install the dependencies:
```bash
pip install -r requirements.txt
```

### 5. Set up environment variables:
Create a `.env` file in the root directory with the following contents:
```bash
FLASK_APP=run.py
FLASK_ENV=development
SQLALCHEMY_DATABASE_URI=your_database_uri_here
SECRET_KEY=your_secret_key_here
SECURITY_PASSWORD_SALT=your_security_password_salt_here
MAIL_USERNAME=your-email@example.com
MAIL_PASSWORD=your-email-password
```

### 6. Initialize the database:

1. Open a Python shell:
   ```bash
   python
   ```

2. In the Python shell, run the following command to create all the necessary tables based on your models:
   ```python
   from market import db
   db.create_all()  # Create the new clean database
   ```

### 7. Run the application:
To run the application, use the `run.py` file as the entry point:
```bash
python run.py
```

The application will be accessible at `http://127.0.0.1:5000/`.

---

## Usage

Once the app is running:

- Visit `http://127.0.0.1:5000/` to access the homepage.
- Register a new account and complete the verification process.
- Browse the marketplace and explore different item categories.
- Use filters to narrow down items based on price, location, or delivery options.
- Manage your profile, post new items for sale, or edit your existing listings.

---

## Folder Structure

```
├── instance/
└── market/
    ├── errors/
    ├── items/
    ├── main/
    ├── static/
    │   ├── images/
    │   ├── image_pics/
    │   │   ├── 1/
    │   │   └── 2/
    │   ├── material/
    │   └── profile_pics/
    │       └── default/
    ├── templates/
    │   ├── errors/
    │   └── modals/
    ├── users/
    └── __pycache__/
```

The application follows a **blueprint structure** where each module (like `errors`, `items`, `main`, `users`) is organized into its own directory. The `run.py` file serves as the entry point for the application.

---

## Marketplace Overview

The marketplace page displays items in categories such as **Electronics** and **Clothes**. Users can filter items by price, location, and delivery options. Listings show item details like images, price, and seller information.

---

## Authentication and Security

- **Flask-Login** is used for secure session handling and user authentication.
- Passwords are hashed using **Flask-Bcrypt**.
- **Flask-Limiter** is implemented to rate-limit login attempts and protect against brute-force attacks.
- Security best practices such as HTTPS, CSRF protection (via **Flask-WTF**), and input validation are followed.

---

## Email Integration

The app uses **Flask-Mail** for email-based functionalities:
- **Account Verification**: A verification link is sent upon registration.
- **Password Reset**: A secure token is generated to reset a user's password.

To set up **Flask-Mail**, add the relevant email configuration to your `.env` file:
```bash
MAIL_SERVER=smtp.your-mail-provider.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@example.com
MAIL_PASSWORD=your-email-password
```

---

## Frontend and Styling

The frontend is built using **Bootstrap** for responsiveness and consistency across devices. Key styling features include:
- **Fixed Top Navigation Bar**: Red, black, and white theme.
- **Minimalistic Filter Form**: Filter options for searching items.
- **Dynamic Elements**: Smooth transitions using **JavaScript**.
- **Background Image**: A blurred image (engine-akyurt-T8-pETMmHCE-unsplash) enhances the overall design.

## Support

For technical support, please refer to the documentation provided or contact support at **almazghony@gmail.com** or simply contact me directly on whatsapp **01559920152** for further assistance.

---