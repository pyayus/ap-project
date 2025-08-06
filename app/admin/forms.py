from flask_wtf import FlaskForm
from wtforms import (
    PasswordField,
    StringField,
    IntegerField,
    SubmitField,
    TextAreaField,
    FieldList,
    FormField,
    DateTimeLocalField,
)
from wtforms.validators import StopValidation, DataRequired
from ..models import CourseInterval


class AdminRegisterForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Register admin")


class UserRemoveForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    submit = SubmitField("Remove")


class DataRequiredValidateTime:
    def __init__(self, message=None):
        self.message = message

    def __call__(self, form, field):
        if field.data and (not isinstance(field.data, str) or field.data.strip()):
            return

        if self.message is None:
            message = field.gettext("This field is required.")
        else:
            message = self.message

        field.errors[:] = []
        raise StopValidation(message)


class CoursePrerequisiteForm(FlaskForm):
    prerequisite = StringField("Prerequisite")
    remove = SubmitField("Remove")


class TimeMDForm(FlaskForm):
    month = IntegerField("Month")
    day = IntegerField("Day")

    def _fields_or_zero(self):
        return (self.month.data or 0, self.day.data or 0)

    def to_seconds(self):
        m, d = self._fields_or_zero()
        return m * 2592000 + d * 86400

    def validate(self, extra_validators=None):
        if not super().validate(extra_validators):
            return False

        m, d = self._fields_or_zero()
        if m < 0 or d < 0:
            return False
        if m == 0 and d == 0:
            return False


class TimeHMForm(FlaskForm):
    hour = IntegerField("Hour")
    minutes = IntegerField("Minutes")

    def _fields_or_zero(self):
        return (self.hour.data or 0, self.minutes.data or 0)

    def to_seconds(self):
        h, m = self._fields_or_zero()
        return h * 3600 + m

    def validate(self, extra_validators=None):
        if not super().validate(extra_validators):
            return False

        h, m = self._fields_or_zero()
        if h < 0 or m < 0:
            return False
        if h == 0 and m == 0:
            return False


class CourseIntervalForm(FlaskForm):
    start = DateTimeLocalField("Start", validators=[DataRequiredValidateTime()])
    end = DateTimeLocalField("End", validators=[DataRequiredValidateTime()])
    every = FormField(TimeMDForm)
    duration = FormField(TimeHMForm)
    remove = SubmitField("Remove")

    def to_interval_model(self, course_id):
        return CourseInterval(
            course_id,
            self.start.data.timestamp(),
            self.end.data.timestamp(),
            self.every.form.to_seconds(),
            self.duration.form.to_seconds(),
        )


class AddCourseForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    description = TextAreaField("Description")
    capacity = IntegerField("Capacity", validators=[DataRequired()])
    intervals = FieldList(FormField(CourseIntervalForm))
    add_interval = SubmitField("Add interval")
    prerequisites = FieldList(FormField(CoursePrerequisiteForm))
    add_prerequisite = SubmitField("Add prerequisite")
    submit = SubmitField("Add")
