# initialize_db.py

from app import create_app, db
from app.models import User, Ticket
import os
from config_app import DevConfig, ProdConfig

print("Initializing the app...")

config_class = DevConfig if os.getenv('FLASK_ENV') == 'development' else ProdConfig
app = create_app(config_class)

print("App created with config:", config_class)

with app.app_context():
    print("App context established.")
    try:
        db.create_all()
        print("Database tables created.")
    except Exception as e:
        print(f"Error creating database tables: {e}")

    admin_username = os.getenv('INITIAL_USER', 'admin')
    admin_password = os.getenv('INITIAL_PASSWORD', 'SonnysAndon2024')

    try:
        user_query = User.query.filter_by(username=admin_username).first()
        print(f"Query executed. Result: {user_query}")
    except Exception as e:
        print(f"Error executing query: {e}")
        user_query = None

    if user_query is None:
        try:
            admin = User(username=admin_username)
            admin.set_password(admin_password)
            db.session.add(admin)
            db.session.commit()
            print(f"Created initial admin user: {admin_username}")
        except Exception as e:
            print(f"Error creating admin user: {e}")
    else:
        print(f"Admin user {admin_username} already exists")
