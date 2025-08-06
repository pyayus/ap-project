from flask import flash, render_template, redirect, url_for
from flask_login import login_required, current_user
from wtforms import Label
from . import course
from .forms import CourseSearchForm
from ..models import Course, CoursePrerequisite, CourseInterval, UserCourse
from ..database import db
from ..default_admin import DEFAULT_ADMIN_ID
from ..util import find_first, retain, take_n, timestamp_to_str


@course.route("/course", methods=["GET", "POST"])
@login_required
def courses():
    search = CourseSearchForm()

    if search.validate_on_submit():
        courses = (
            db.session.query(Course)
            .filter(
                Course.name.contains(search.query.data, autoescape=True)
                | Course.description.contains(search.query.data, autoescape=True)
            )
            .limit(100)
            .all()
        )
    else:
        courses = db.session.query(Course).limit(100).all()
    user_courses = db.session.query(UserCourse).filter_by(user_id=current_user.id).all()
    user_course_intervals = [
        db.session.query(CourseInterval).filter_by(course_id=uc.course_id).all()
        for uc in user_courses
    ]

    def can_attend_course(course_info):
        for uc in user_course_intervals:
            for uci in uc:
                for i in course_info.intervals:
                    if uci.has_intersection(i):
                        return False
        return True

    courses = list(take_n(20, filter(can_attend_course, courses)))
    return render_template(
        "courses.html",
        search=search,
        courses=courses,
        timestamp_to_str=timestamp_to_str,
    )


@course.route("/course/<int:id>")
@login_required
def course_view(id):
    course = db.session.query(Course).filter_by(id=id).one_or_none()
    if course is None:
        return "Not found", 404

    course_occupation = db.session.query(UserCourse).filter_by(course_id=id).count()

    user_has_course = (
        db.session.query(UserCourse)
        .filter_by(course_id=id, user_id=current_user.id)
        .count()
    )

    return render_template(
        "course_view.html",
        user=current_user,
        course=course,
        course_occupation=course_occupation,
        user_has_course=user_has_course,
        timestamp_to_str=timestamp_to_str,
    )


@course.route("/course/<int:id>/add")
@login_required
def add_course(id):
    if current_user.id == DEFAULT_ADMIN_ID:
        return "Cannot add courses to the default admin user"

    course = db.session.query(Course).filter_by(id=id).one_or_none()
    if course is None:
        return "Not found", 404

    if any(uc.id == id for uc in current_user.courses):
        flash("This course has already been added")
        return redirect(url_for("course.course_view", id=id))

    user_courses = [
        db.session.query(Course).filter_by(id=course.course_id).one()
        for course in current_user.courses
    ]

    if any(course.intersects_with(uc) for uc in user_courses):
        flash("You cannot add this course as it collides with another course's time")
        return redirect(url_for("course.course_view", id=id))

    user_course = UserCourse(current_user.id, course.id)
    db.session.add(user_course)
    db.session.commit()

    current_user.courses.append(user_course)
    db.session.commit()

    flash("Course has been added")
    return redirect(url_for("course.course_view", id=id))


@course.route("/course/<int:id>/remove")
@login_required
def remove_course(id):
    if current_user.id == DEFAULT_ADMIN_ID:
        return "Cannot remove courses from the default admin user"

    course = db.session.query(Course).filter_by(id=id).one_or_none()
    if course is None:
        return "Not found", 404

    # if not any(uc.id == id for uc in current_user.courses):
    #     flash("You don't have this course added")
    #     return redirect(url_for("course.course_view", id=id))

    deleted = (
        db.session.query(UserCourse)
        .filter_by(course_id=id, user_id=current_user.id)
        .delete()
    )
    if deleted == 0:
        flash("You don't have this course added")
        return redirect(url_for("course.course_view", id=id))
    retain(lambda c: c.course_id != id, current_user.courses)
    db.session.commit()

    flash("Course has been removed")
    return redirect(url_for("course.course_view", id=id))
