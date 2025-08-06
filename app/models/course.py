import json
from typing import List
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import TypeDecorator, String

from ..database import db


class CourseInterval(db.Model):
    __tablename__ = "course_interval"

    id: Mapped[int] = mapped_column(primary_key=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("course.id"))
    start: Mapped[int]
    end: Mapped[int]
    delay: Mapped[int]
    duration: Mapped[int]

    def __init__(self, course_id, start, end, delay, duration):
        self.course_id = course_id
        self.start = start
        self.end = end
        self.delay = delay
        self.duration = duration

    def _time_is_inside(self, t):
        return (t - self.start) % self.delay < self.duration

    def _next_edge_dt(self, t):
        tl = (t - self.start) % self.delay
        if tl < self.duration:
            return self.duration - tl
        else:
            return self.delay - tl

    def has_intersection(self, other):
        t = max(self.start, other.start)
        t_end = min(self.end, other.end)
        while t <= t_end:
            if self._time_is_inside(t) and other._time_is_inside(t):
                return True
            t += min(self._next_edge_dt(t), other._next_edge_dt(t))
        return False


class CoursePrerequisite(db.Model):
    __tablename__ = "course_prerequisite"

    id: Mapped[int] = mapped_column(primary_key=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("course.id"))
    prerequisite: Mapped[str]

    def __init__(self, course_id, prerequisite):
        self.course_id = course_id
        self.prerequisite = prerequisite


class Course(db.Model):
    __tablename__ = "course"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    description: Mapped[str]
    capacity: Mapped[int]
    prerequisites: Mapped[List["CoursePrerequisite"]] = relationship(
        cascade="all, delete-orphan"
    )
    intervals: Mapped[List["CourseInterval"]] = relationship(
        cascade="all, delete-orphan"
    )

    def __init__(self, name, description, capacity, prerequisites, intervals):
        self.name = name
        self.description = description
        self.capacity = capacity
        self.prerequisites = prerequisites
        self.intervals = intervals
    
    def intersects_with(self, other):
        return any(s.has_intersection(o) for o in other.intervals for s in self.intervals)