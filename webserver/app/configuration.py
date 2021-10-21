# SPDX-License-Identifier: Zlib
#
# Copyright (c) 2021 Antonio Niño Díaz

import os

from configparser import ConfigParser

from app import app

FILENAME_CONFIG = "/home/" + app.config["USERNAME"] + "/configuration.ini"

DEFAULT_MAX_ATTENDEES = 10


def Configuration_Clear():
    # Delete file if it exists
    if os.path.exists(DATABASE_PATH):
        os.remove(DATABASE_PATH)


def Configuration_MaxAttendees_Set(num):
    config = ConfigParser()
    config.read(FILENAME_CONFIG)
    if not config.has_section('general'):
        config.add_section('general')
    config.set('general', 'max_attendees', str(num))
    with open(FILENAME_CONFIG, 'w') as f:
        config.write(f)


def Configuration_MaxAttendees_Get():
    config = ConfigParser()
    config.read(FILENAME_CONFIG)
    val = DEFAULT_MAX_ATTENDEES
    try:
        val_str = config.get('general', 'max_attendees')
        val = int(val_str)
    except:
        pass
    return val
