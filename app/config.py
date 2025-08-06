import os


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "default_secret_key"
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or "sqlite:///database.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEFAULT_ADMIN_ENABLED = (os.environ.get("DEFAULT_ADMIN_ENABLED") or "1") != "0"
    DEFAULT_ADMIN_PASSWORD = os.environ.get("DEFAULT_ADMIN_PASSWORD") or "pass"
