from flask_wtf import FlaskForm
from wtforms import SearchField, SubmitField


class CourseSearchForm(FlaskForm):
    query = SearchField("Search course")
    submit = SubmitField("Search")
