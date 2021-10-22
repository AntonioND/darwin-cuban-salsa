# SPDX-License-Identifier: Zlib
#
# Copyright (c) 2021 Antonio Niño Díaz

import os

from datetime import datetime
from flask import request, session

from app import app

FILENAME_LOG = "/home/" + app.config["USERNAME"] + "/event_log.txt"


def LogEvent_GetPath():
    return FILENAME_LOG


def LogEvent_Clear():
    if os.path.exists(FILENAME_LOG):
        os.remove(FILENAME_LOG)


def LogEvent_WriteContext(f):
    date_time_now = datetime.now()
    time_str = date_time_now.strftime("%Y/%m/%d %H:%M:%S")
    f.write(time_str + ' || ' + request.remote_addr + '\n')

    try:
        f.write(request.headers.get('User-Agent') + '\n')
    except:
        f.write('User-Agent: Not found')

    try:
        f.write(request.headers.get('Accept-Language') + '\n')
    except:
        f.write('Accept-Language: Not found')

    f.write('csrf_token: ')
    try:
        f.write(session.get('csrf_token') + '\n')
    except:
        f.write('Not found')


def LogEvent_Result(result):
    with open(FILENAME_LOG, "a") as f:
        f.write(result)


def LogEvent_BookLesson(name, identifier, wants_rueda, is_darwin):
    with open(FILENAME_LOG, "a") as f:
        f.write("\n\n")
        LogEvent_WriteContext(f)
        f.write('BOOK({}, {}, {}, {}): '. format(
                name, identifier, wants_rueda, is_darwin))


def LogEvent_CheckBooking(identifier):
    with open(FILENAME_LOG, "a") as f:
        f.write("\n\n")
        LogEvent_WriteContext(f)
        f.write('CHECK({}): '. format(identifier))


def LogEvent_CancelBooking(identifier):
    with open(FILENAME_LOG, "a") as f:
        f.write("\n\n")
        LogEvent_WriteContext(f)
        f.write('CANCEL({}): '. format(identifier))


def LogEvent_Admin(event):
    with open(FILENAME_LOG, "a") as f:
        f.write("\n\n")
        LogEvent_WriteContext(f)
        f.write('ADMIN: ' + event + '\n')


def LogEvent_AdminInvalidPassword(password):
    with open(FILENAME_LOG, "a") as f:
        f.write("\n\n")
        LogEvent_WriteContext(f)
        f.write('ADMIN: INVALID PASSWORD: "{}"'. format(password))
