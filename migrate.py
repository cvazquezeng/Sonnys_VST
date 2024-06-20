import os
from dotenv import load_dotenv
from flask import Flask
from flask_migrate import Migrate
from app import create_app, db
from config_app import DevConfig, ProdConfig

load_dotenv()  # Load environment variables from .env file

config_class = DevConfig if os.environ.get('FLASK_ENV') == 'development' else ProdConfig
app = create_app(config_class)
migrate = Migrate(app, db)

@app.cli.command("init_db")
def init_db():
    db.create_all()
    print("Initialized the database")
