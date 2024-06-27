# config_app.py
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'mysql+pymysql://cvazquez:Sonnys2024@db/andon'
    #SQLALCHEMY_ECHO = True  # Enable query logging


class DevConfig(Config):
    DEBUG = True

class ProdConfig(Config):
    DEBUG = False