import html
from flask import render_template
from flask_login import current_user, login_required

from . import dashboard
from .forms import CourseSearchForm
from ..database import db
from ..models import User, UserCourse, Course
from ..util import timestamp_to_str


@dashboard.route("/dashboard")
def index():
    return render_template("dashboard.html")


@dashboard.route("/my_courses")
def my_courses():
    user_courses = [
        db.session.query(Course).filter_by(id=uc.course_id).one()
        for uc in current_user.courses
    ]

    search = CourseSearchForm()
    if search.validate_on_submit():
        courses = list(
            filter(
                lambda course: course.name.includes(search.data)
                or course.description.includes(search.data),
                user_courses,
            )
        )
    else:
        courses = user_courses

    return render_template(
        "my_courses.html",
        search=search,
        courses=courses,
        timestamp_to_str=timestamp_to_str,
    )
