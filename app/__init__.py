# app/__init__.py
from flask import Flask, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_caching import Cache

import logging

db = SQLAlchemy()
login_manager = LoginManager()
cache = Cache()

def create_app(config_class):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    cache.init_app(app, config={'CACHE_TYPE': 'simple'})
    login_manager.login_view = 'auth.login'

    # Setup logging
    logging.basicConfig(level=logging.DEBUG)

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from .routes.auth import auth_bp
    from .routes.main import main_bp
    from .routes.api import api_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp)  # Ensure this is registered only once

    @app.after_request
    def add_header(response):
        response.cache_control.no_store = True
        return response

    @app.route('/static/<path:filename>')
    @cache.cached(timeout=3600)
    def cached_static(filename):
        return send_from_directory('static', filename)

    return app
