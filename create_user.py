import os
from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    username = os.environ.get('INITIAL_USER', 'admin')
    password = os.environ.get('INITIAL_PASSWORD', 'SonnysAndon2024')

    user = User.query.filter_by(username=username).first()
    if not user:
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        user = User(username=username, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        print(f"User {username} created with hashed password.")
    else:
        print(f"User {username} already exists.")
