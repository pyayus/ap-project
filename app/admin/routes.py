from functools import wraps
from flask import redirect, render_template, flash, url_for

from . import admin
from .forms import AddCourseForm, AdminRegisterForm, UserRemoveForm
from ..models import UserPermission, Course, CoursePrerequisite
from ..database import db
from ..util import retain
from ..default_admin import DEFAULT_ADMIN_USERNAME
from ..models.user import User, UserCourse


def admin_required(func):
    from flask_login import current_user, login_required

    @wraps(func)
    def inner():
        if current_user.permission.value >= UserPermission.Admin.value:
            return func()
        else:
            return "You need to be an admin to access this page.", 401

    return login_required(inner)


@admin.route("/admin")
@admin_required
def index_redirect():
    return redirect(url_for("admin.dashboard"))


@admin.route("/admin/dashboard")
@admin_required
def dashboard():
    return render_template("admin_dashboard.html")


@admin.route("/admin/register_admin", methods=["GET", "POST"])
@admin_required
def register_admin():
    form = AdminRegisterForm()
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
                new_user = User.make_user(
                    form.username.data, form.password.data, UserPermission.Admin
                )
                db.session.add(new_user)
                db.session.commit()
                flash("Registered successfully")
                return redirect(url_for("admin.register_admin"))
            else:
                flash("This username is already taken")
    return render_template("admin_register.html", form=form)


@admin.route("/admin/remove_user", methods=["GET", "POST"])
@admin_required
def remove_user():
    form = UserRemoveForm()
    if form.validate_on_submit():
        if form.username.data == DEFAULT_ADMIN_USERNAME:
            return "Set the DEFAULT_ADMIN_ENABLED environment variable to 0 to disable the default admin user."
        deleted = (
            db.session.query(User).filter_by(username=form.username.data).delete() != 0
        )
        db.session.commit()
        if not deleted:
            flash("No such user")
        else:
            flash("User removed successfully")
    return render_template("admin_user_remove.html", form=form)


@admin.route("/admin/add_course", methods=["GET", "POST"])
@admin_required
def add_course():
    form = AddCourseForm()
    if form.add_interval.data:
        form.intervals.append_entry(None)
    elif form.add_prerequisite.data:
        form.prerequisites.append_entry(None)
    elif any(r.form.remove.data for r in form.intervals):
        retain(lambda f: not f.form.remove.data, form.intervals.entries)
    elif any(r.form.remove.data for r in form.prerequisites):
        retain(lambda f: not f.form.remove.data, form.prerequisites.entries)
    elif form.validate_on_submit():
        course = Course(
            form.name.data, form.description.data, form.capacity.data, [], []
        )
        db.session.add(course)
        db.session.commit()
        prerequisites = [
            CoursePrerequisite(course.id, r.form.prerequisite.data)
            for r in form.prerequisites
        ]
        intervals = [i.form.to_interval_model(course.id) for i in form.intervals]
        db.session.add_all(prerequisites)
        db.session.add_all(intervals)
        db.session.commit()
        course.prerequisites = prerequisites
        course.intervals = intervals
        db.session.commit()
        flash("Course added successfully")
    elif len(form.errors) != 0:
        flash(str(form.errors))
    return render_template("add_course.html", form=form)


@admin.route("/admin/delete_course/<int:id>", methods=["GET", "POST"])
@admin_required
def delete_course(id):
    deleted = db.session.query(Course).filter_by(id=id).delete() != 0
    if not deleted:
        db.session.commit()
        flash("No such course exists")
        return redirect(url_for("course.courses"))
    db.session.query(UserCourse).filter_by(course_id=id).delete()
    db.session.commit()
    flash("Course deleted successfully")
    return redirect(url_for("course.courses"))
