# usercreation.py

from app import create_app, db
from app.models import User

def create_user(config_class, username, password, role):
    app = create_app(config_class)
    with app.app_context():
        # Check if user already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            print(f"User {username} already exists.")
            return

        # Create new user
        new_user = User(username=username, role=role)  # Added role field
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        print(f"User {username} with role {role} created successfully.")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Create a new user.")
    parser.add_argument("config_class", help="The configuration class for the Flask app")
    parser.add_argument("username", help="The username of the new user")
    parser.add_argument("password", help="The password for the new user")
    parser.add_argument("role", help="The role for the new user")  # Added role argument

    args = parser.parse_args()

    # Assume the config_class is given as config_app.Config
    config_class_path = args.config_class
    create_user(config_class_path, args.username, args.password, args.role)
