# SPDX-License-Identifier: Zlib
#
# Copyright (c) 2021-2022 Antonio Niño Díaz

from datetime import datetime

import sqlite3
import os
#import time

DATABASE_PATH = "/home/" + os.environ.get('USER') + "/attendees.db"

def today_is_weekday_in(weekdays):
    """Returns True if today is one of the specified weekdays."""
    today = datetime.now()
    return today.weekday() in weekdays

def DatabaseReset():
    # Delete database if it already exists
    if os.path.exists(DATABASE_PATH):
        os.remove(DATABASE_PATH)

    # Create new database
    con = sqlite3.connect(DATABASE_PATH)
    with con:
        con.execute("""
            CREATE TABLE attendees (
                number INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                identifier TEXT NOT NULL,
                is_darwin STRING
            );
        """)
        con.commit()

if today_is_weekday_in([2, 3]):
    DatabaseReset()
