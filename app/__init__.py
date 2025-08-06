from flask import Flask
from .config import Config
from .database import db
from .login import login_manager

from .admin import admin as admin_blueprint
from .auth import auth as auth_blueprint
from .course import course as course_blueprint
from .dashboard import dashboard as dashboard_blueprint
from .home import home as home_blueprint


def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)

    db.init_app(app)

    with app.app_context():
        db.create_all()

    login_manager.init_app(app)

    app.register_blueprint(admin_blueprint)
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(course_blueprint)
    app.register_blueprint(dashboard_blueprint)
    app.register_blueprint(home_blueprint)

    return app
