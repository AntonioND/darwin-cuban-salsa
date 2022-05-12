# SPDX-License-Identifier: Zlib
#
# Copyright (c) 2021-2022 Antonio Niño Díaz

from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired()])
    identifier = StringField('CRSid or Email (e.g.: abc123, example@gmail.com)',
                             validators=[DataRequired()])
    is_darwin = BooleanField('Tick this if you are a Darwin Student')
    submit = SubmitField('Book Lesson')


class CheckForm(FlaskForm):
    identifier = StringField('CRSid or Email (e.g.: abc123, example@gmail.com)',
                             validators=[DataRequired()])
    submit = SubmitField('Check Booking')


class CancelForm(FlaskForm):
    identifier = StringField('CRSid or Email (e.g.: abc123, example@gmail.com)',
                             validators=[DataRequired()])
    submit = SubmitField('Cancel Booking')


class AdminDatabaseForm(FlaskForm):
    password = StringField('Password (needed before pressing any other button)',
                           validators=[DataRequired()])
    download_database = SubmitField('Download list of attendees as CSV file')
    delete_non_darwin = SubmitField('Delete non-darwin attendees from list')
    database_reset = SubmitField('Delete all attendees from list')
    number_attendees = StringField('Number of attendees (can be changed anytime)')
    update_number_attendees = SubmitField('Set the max number of attendees')


class AdminEventLogForm(FlaskForm):
    password = StringField('Password (needed before pressing any other button)',
                           validators=[DataRequired()])
    download_log = SubmitField('Download log of web server events')
    delete_log = SubmitField('Delete log of web server events')
