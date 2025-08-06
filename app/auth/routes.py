import logging
from flask import render_template, session, redirect, url_for, flash
from flask_login import current_user, login_user, logout_user, login_required

from . import auth
from .forms import LoginForm, RegisterForm
from ..models import User
from ..database import db
from ..config import Config
from ..default_admin import DEFAULT_ADMIN_USERNAME, DEFAULT_ADMIN_USER


@auth.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.username.data == DEFAULT_ADMIN_USERNAME:
            if (
                Config.DEFAULT_ADMIN_ENABLED
                and form.password.data == Config.DEFAULT_ADMIN_PASSWORD
            ):
                logging.warning("login with default admin user")
                login_user(DEFAULT_ADMIN_USER)
                return redirect(url_for("admin.dashboard"))
            else:
                flash("Invalid username or password")
        else:
            # user = db.session.execute(
            #     db.select(User).filter_by(username=form.username.data)
            # ).scalar_one_or_none()
            user = (
                db.session.query(User)
                .filter_by(username=form.username.data)
                .one_or_none()
            )
            if user and user.check_password(form.password.data):
                logout_user()
                login_user(user)
                return redirect(url_for("dashboard.index"))
            else:
                flash("Invalid username or password")
    return render_template("login.html", form=form)


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home.index"))


@auth.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.username.data == DEFAULT_ADMIN_USERNAME:
            flash("This username is already taken")
        else:
            user = (
                db.session.query(User)
                .filter_by(username=form.username.data)
                .one_or_none()
            )
            if user is None:
                new_user = User.make_user(form.username.data, form.password.data)
                db.session.add(new_user)
                db.session.commit()
                flash("Registered successfully")
                return redirect(url_for("dashboard.index"))
            else:
                flash("This username is already taken")
    return render_template("register.html", form=form)


@auth.route("/unregister")
@login_required
def unregister():
    if current_user.username == DEFAULT_ADMIN_USERNAME:
        return "Set the DEFAULT_ADMIN_ENABLED environment variable to 0 to disable the default admin user."
    db.session.delete(current_user)
    db.session.commit()
    logout_user()
    return redirect(url_for("home.index"))
