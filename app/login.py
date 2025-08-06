import flask_login

from .database import db
from .models.user import User
from .config import Config
from .default_admin import DEFAULT_ADMIN_ID, DEFAULT_ADMIN_USER

login_manager = flask_login.LoginManager()


@login_manager.user_loader
def user_loader(id):
    if id == DEFAULT_ADMIN_ID:
        return DEFAULT_ADMIN_USER if Config.DEFAULT_ADMIN_ENABLED else None
    
    return db.session.query(User).filter_by(id=id).one_or_none()


@login_manager.unauthorized_handler
def unauthorized_handler():
    return "Unauthorized", 401
