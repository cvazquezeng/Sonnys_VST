# app/__init__.py
from flask import Flask, send_from_directory, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_caching import Cache
from apscheduler.schedulers.background import BackgroundScheduler
from flask_migrate import Migrate

import logging

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
cache = Cache()
scheduler = BackgroundScheduler()

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

    with app.app_context():
        from .models import User, Ticket  # Import models after app context is set

        @login_manager.user_loader
        def load_user(user_id):
            return User.query.get(int(user_id))

        from .routes.auth import auth_bp
        from .routes.main import main_bp
        from .routes.api import api_bp

        app.register_blueprint(auth_bp)
        app.register_blueprint(main_bp)
        app.register_blueprint(api_bp)

        @app.after_request
        def add_header(response):
            response.cache_control.no_store = True
            return response

        @app.route('/static/<path:filename>')
        @cache.cached(timeout=3600)
        def cached_static(filename):
            return send_from_directory('static', filename)

    # Schedule the save_tickets job
    from .tasks import save_tickets
    scheduler.add_job(func=save_tickets, args=[app], trigger="interval", seconds=30, id="save_tickets", replace_existing=True)
    
    # Schedule the update_tickets job
    from .tasks import update_tickets
    scheduler.add_job(func=update_tickets, args=[app], trigger="interval", seconds=720, id="update_tickets", replace_existing=True)
    
    scheduler.start()
    
    return app
