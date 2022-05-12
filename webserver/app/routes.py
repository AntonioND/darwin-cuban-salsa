# SPDX-License-Identifier: Zlib
#
# Copyright (c) 2021-2022 Antonio Niño Díaz

from datetime import datetime, timedelta
from flask import render_template, flash, redirect, request, send_file, url_for

from app import app
from app.forms import *
from app.configuration import *
from app.database import *
from app.logger import *

# This is needed to make accesses to databases thread and process-safe
if os.environ.get("DEBUG") == "true":
    def lock_get():
        pass

    def lock_release():
        pass
else:
    import uwsgi

    def lock_get():
        uwsgi.lock()

    def lock_release():
        uwsgi.unlock()


FILENAME_TEMP = "/home/" + app.config["USERNAME"] + "/temp.csv"


def validate_name(string):
    for char in string:
        if char.isalnum() or char in " -.":
            continue
        return False
    return True


def validate_identifier(string):
    for char in string:
        if char.isalnum() or char in "@._-":
            continue
        return False
    return True


def today_is_weekday_in(weekdays):
    """Returns True if today is one of the specified weekdays."""
    today = datetime.now()
    return today.weekday() in weekdays


def next_weekday(weekday):
    """Returns a datetime object with the next specified weekday."""
    today = datetime.now()
    days_ahead = (weekday - today.weekday()) % 7
    return today + timedelta(days_ahead)


@app.route('/')
@app.route('/index')
def index():
    attendees = 0
    waitlist = 0

    lock_get()
    try:
        total = DatabaseGetSize()
    finally:
        lock_release()

    max_attendees = Configuration_MaxAttendees_Get()
    if total > max_attendees:
        attendees = max_attendees
        waitlist = total - max_attendees
    else:
        attendees = total

    tuesday = next_weekday(1)
    tuesday_str = tuesday.strftime("%Y/%m/%d")

    count = {
        'attendees': str(attendees),
        'waitlist': str(waitlist),
        'max_attendees': str(max_attendees),
        'lesson_date': str(tuesday_str)
    }

    return render_template('index.html', title='Home', count=count)


MSG_COMMON = "Bookings open on Friday at 17:00 and end on Tuesday at 19:00"

MSG_DARWIN = ("Darwin member: " +
             "Bookings open on Friday at 17:00 and end on Tuesday at 19:00")

MSG_NON_DARWIN = ("Not a Darwin member: " +
                 "Bookings open on Sunday at 22:00 and end on Tuesday at 19:00")


def check_booking_time(is_darwin):
    # First, check weekday
    if is_darwin == "Yes":
        # Darwin: Fridays, Saturdays, Sundays, Mondays and Tuesdays
        if not today_is_weekday_in([4, 5, 6, 0, 1]):
            flash(MSG_DARWIN)
            return (False, 'Bookings closed - Darwin (1)')

        # If it is Friday, only allow bookings after 17:00
        if today_is_weekday_in([4]) and datetime.now().hour < 17:
            flash(MSG_DARWIN)
            return (False, 'Bookings closed - Darwin (2)')
    else:
        # Non-Darwin: Only Mondays and Tuesdays are allowed
        if not today_is_weekday_in([6, 0, 1]):
            flash(MSG_NON_DARWIN)
            return (False, 'Bookings closed - Non Darwin (1)')

        # If it is Sunday, only allow bookings after 22:00
        if today_is_weekday_in([6]) and datetime.now().hour < 22:
            flash(MSG_NON_DARWIN)
            return (False, 'Bookings closed - Non Darwin (2)')

    # If it is Tuesday, only allow bookings until 19:00
    if today_is_weekday_in([1]) and datetime.now().hour >= 19:
        flash(MSG_COMMON)
        return (False, 'Bookings closed - Common (1)')

    return (True, None)


def check_cancel_time():
    # Fridays, Saturdays, Sundays, Mondays and Tuesdays
    if not today_is_weekday_in([4, 5, 6, 0, 1]):
        flash(MSG_COMMON)
        return (False, 'Bookings closed (1)')

    # If it is Friday, only allow bookings after 17:00
    if today_is_weekday_in([4]) and datetime.now().hour < 17:
        flash(MSG_COMMON)
        return (False, 'Bookings closed (2)')

    # If it is Tuesday, only allow booking cancellations until 19:00
    if today_is_weekday_in([1]) and datetime.now().hour >= 19:
        flash(MSG_COMMON)
        return (False, 'Bookings closed (3)')

    return (True, None)


def book_lesson_internal(full_name, identifier, is_darwin):

    ok, error_str = check_booking_time(is_darwin)
    if not ok:
        return error_str

    # Validate user input fields
    valid_fields = True
    if not validate_name(full_name):
        flash("Invalid characters in name")
        valid_fields = False
    if not validate_identifier(identifier):
        flash("Invalid characters in email/CRSid")
        valid_fields = False

    if not valid_fields:
        return 'Invalid fields'

    # Is this name already registered?
    index = DatabaseGetIndex(identifier)
    if index != -1:
        flash('Already registered')
        flash('CRSid/Email: {}'.format(identifier))
        return 'Already registered'

    ok = DatabaseAdd(full_name, identifier, is_darwin)
    if not ok:
        flash('Failed to register')
        flash('CRSid/Email: {}'.format(identifier))
        return 'Failed to register'

    index = DatabaseGetIndex(identifier)
    if index == -1:
        flash('Failed to verify registration')
        return 'Failed to verify'

    flash('Registration complete')
    flash('Name: {} | CRSid/Email: {} | Darwin: {}'.format(
          full_name, identifier, is_darwin))

    max_attendees = Configuration_MaxAttendees_Get()
    if index > max_attendees:
        number = index - max_attendees
        flash("You are in the wait list! You're number {}".format(number))
    else:
        flash("You can attend the lesson!")

    return 'Success'


@app.route('/book_lesson', methods=['GET', 'POST'])
def book_lesson():
    form = LoginForm()
    if form.validate_on_submit():
        identifier = form.identifier.data
        identifier = identifier.replace(" ", "")
        identifier = identifier.lower()

        lock_get()
        try:
            full_name = form.full_name.data
            is_darwin = "Yes" if form.is_darwin.data else "No"
            LogEvent_BookLesson(full_name, identifier, is_darwin)
            result = book_lesson_internal(full_name, identifier, is_darwin)
            LogEvent_Result(result)
        finally:
            lock_release()

    return render_template('book_lesson.html', title='Book Lesson', form=form)


def check_booking_internal(identifier):
    # Validate user input fields
    valid_fields = True
    if not validate_identifier(identifier):
        flash("Invalid characters in email/CRSid")
        valid_fields = False

    if not valid_fields:
        return 'Invalid fields'

    index = DatabaseGetIndex(identifier)
    if index == -1:
        flash('Not found')
        flash('CRSid/Email: {}'.format(identifier))
        return 'Not found'

    max_attendees = Configuration_MaxAttendees_Get()
    if index > max_attendees:
        number = index - max_attendees
        flash("You are in the wait list! You're number {}".format(number))
    else:
        flash("You can attend the lesson!")
    flash('CRSid/Email: {}'.format(identifier))

    return 'Success'


@app.route('/check_booking', methods=['GET', 'POST'])
def check_booking():
    form = CheckForm()
    if form.validate_on_submit():
        identifier = form.identifier.data
        identifier = identifier.replace(" ", "")
        identifier = identifier.lower()

        lock_get()
        try:
            LogEvent_CheckBooking(identifier)
            result = check_booking_internal(identifier)
            LogEvent_Result(result)
        finally:
            lock_release()

    return render_template('check_booking.html', title='Check Booking',
                           form=form)


def cancel_booking_internal(identifier):

    ok, error_str = check_cancel_time()
    if not ok:
        return error_str

    # Validate user input fields
    valid_fields = True
    if not validate_identifier(identifier):
        flash("Invalid characters in email/CRSid")
        valid_fields = False

    if not valid_fields:
        return 'Invalid fields'

    index = DatabaseGetIndex(identifier)
    if index == -1:
        flash('Not found')
        flash('CRSid/Email: {}'.format(identifier))
        return 'Not found'

    ok = DatabaseDelete(identifier)
    if not ok:
        flash('Failed to cancel')
        flash('CRSid/Email: {}'.format(identifier))
        return 'Failed to cancel'

    flash('Cancelled')
    flash('CRSid/Email: {}'.format(identifier))

    return 'Success'


@app.route('/cancel_booking', methods=['GET', 'POST'])
def cancel_booking():
    form = CancelForm()
    if form.validate_on_submit():
        identifier = form.identifier.data
        identifier = identifier.replace(" ", "")
        identifier = identifier.lower()

        lock_get()
        try:
            LogEvent_CancelBooking(identifier)
            result = cancel_booking_internal(identifier)
            LogEvent_Result(result)
        finally:
            lock_release()

    return render_template('cancel_booking.html', title='Cancel Booking',
                           form=form)


def check_admin_password_and_print_error(form, password):
    if password == app.config['ADMIN_PASSWORD']:
        return True
    else:
        flash('Invalid password')
        LogEvent_AdminInvalidPassword(form.password.data)
        return False


def admin_database_action(form):
    if form.download_database.data:
        if form.validate():
            if check_admin_password_and_print_error(form, form.password.data):
                LogEvent_Admin('DATABASE DOWNLOAD')
                max_attendees = Configuration_MaxAttendees_Get()
                DatabasePrint(max_attendees, FILENAME_TEMP)
                date_time_now = datetime.now()
                name = date_time_now.strftime("%Y-%m-%d_%H-%M-%S.csv")
                return send_file(FILENAME_TEMP, as_attachment=True,
                                 download_name=name)

    elif form.update_number_attendees.data:
        if form.validate():
            if check_admin_password_and_print_error(form, form.password.data):
                num = 0
                error_str = "Invalid value: it must be between 1 and 300"
                try:
                    num = int(form.number_attendees.data)
                except:
                    pass

                if num >= 1 and num <= 300:
                    Configuration_MaxAttendees_Set(num)
                    flash("Number of attendees set to {}".format(num))
                    LogEvent_Admin('UPDATE NUMBER ATTENDEES: {}'.format(num))
                else:
                    flash(error_str)

    elif form.delete_non_darwin.data:
        if form.validate():
            if check_admin_password_and_print_error(form, form.password.data):
                LogEvent_Admin('DATABASE DELETE NON DARWIN')
                DatabaseDeleteNonDarwin()

    elif form.database_reset.data:
        if form.validate():
            if check_admin_password_and_print_error(form, form.password.data):
                LogEvent_Admin('DATABASE RESET')
                DatabaseReset()

    return render_template('admin_database.html',
                           title='Admin Attendees Database', form=form)


@app.route('/admin/database', methods=['GET', 'POST'])
def admin_database():
    form = AdminDatabaseForm()

    lock_get()
    try:
        return admin_database_action(form)
    finally:
        lock_release()


def admin_event_log_action(form):

    if form.download_log.data:
        if form.validate():
            if check_admin_password_and_print_error(form, form.password.data):
                LogEvent_Admin('LOG DOWNLOAD')
                date_time_now = datetime.now()
                name = date_time_now.strftime("%Y-%m-%d_%H-%M-%S_events.log")
                return send_file(LogEvent_GetPath(), as_attachment=True,
                                 download_name=name)

    elif form.delete_log.data:
        if form.validate():
            if check_admin_password_and_print_error(form, form.password.data):
                LogEvent_Admin('LOG DELETE')
                LogEvent_Clear()

    return render_template('admin_event_log.html', title='Admin Event Log',
                           form=form)


@app.route('/admin/event_log', methods=['GET', 'POST'])
def admin_event_log():
    form = AdminEventLogForm()

    lock_get()
    try:
        return admin_event_log_action(form)
    finally:
        lock_release()


@app.route('/admin', methods=['GET'])
def admin():
    return render_template('admin.html', title='Admin')


# Oops...
@app.route('/xbody', methods=['GET'])
def xbody():
    return "rulz"
