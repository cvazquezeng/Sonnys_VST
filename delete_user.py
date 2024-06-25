# delete_user.py

from app import create_app, db
from app.models import User

def delete_user(config_class, username):
    app = create_app(config_class)
    with app.app_context():
        # Check if user exists
        user = User.query.filter_by(username=username).first()
        if user:
            db.session.delete(user)
            db.session.commit()
            print(f"User {username} deleted successfully.")
        else:
            print(f"User {username} not found.")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Delete a user.")
    parser.add_argument("config_class", help="The configuration class for the Flask app")
    parser.add_argument("username", help="The username of the user to be deleted")

    args = parser.parse_args()

    # Assume the config_class is given as config_app.Config
    config_class_path = args.config_class
    delete_user(config_class_path, args.username)
