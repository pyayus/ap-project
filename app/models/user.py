from enum import Enum
from typing import List
from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from .course import Course
from ..database import db


class UserCourse(db.Model):
    __tablename__ = "user_course"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    course_id: Mapped[int] = mapped_column(ForeignKey("course.id"))

    def __init__(self, user_id, course_id):
        self.user_id = user_id
        self.course_id = course_id


class UserPermission(Enum):
    User = 10
    Admin = 20


class User(db.Model, UserMixin):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    password_hash: Mapped[str]
    courses: Mapped[List["UserCourse"]] = relationship(cascade="all, delete-orphan")
    permission: Mapped[UserPermission]

    def make_user(username, password, permission=UserPermission.User):
        user = User()
        user.username = username
        user.set_password(password)
        user.courses = []
        user.permission = permission
        return user

    def get_id(self):
        return self.id

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        return self.permission.value >= UserPermission.Admin.value
