# SPDX-License-Identifier: Zlib
#
# Copyright (c) 2021 Antonio Niño Díaz

import sqlite3
import os

from app import app

#import time

DATABASE_PATH = "/home/" + app.config["USERNAME"] + "/attendees.db"


def DatabaseExists():
    if os.path.exists(DATABASE_PATH):
        return True
    return False


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
                wants_rueda STRING,
                is_darwin STRING,
                pass_received STRING
            );
        """)
        con.commit()


def DatabaseAdd(full_name, identifier, wants_rueda, is_darwin):
    # Don't allow multiple registrations by the same user
    if DatabaseGetIndex(identifier) != -1:
        return False

    con = sqlite3.connect(DATABASE_PATH)
    with con:
        con.execute("""
            INSERT INTO attendees (name, identifier, wants_rueda, is_darwin, pass_received)
            VALUES ('{}','{}','{}','{}','{}');
        """.format(full_name, identifier, wants_rueda, is_darwin, "-"))
        con.commit()
        #time.sleep(20)

    return True


def DatabaseGetIndex(identifier):
    con = sqlite3.connect(DATABASE_PATH)
    with con:
        rows = con.execute("""
            SELECT * FROM attendees;
        """)
        count = 1
        for r in rows:
            if r[2] == identifier:
                return count
            count += 1
    return -1


def DatabaseDelete(identifier):
    # Fail if the user doesn't exist
    if DatabaseGetIndex(identifier) == -1:
        return False

    con = sqlite3.connect(DATABASE_PATH)
    with con:
        con.execute("""
            DELETE FROM attendees
            WHERE identifier = "{}";
        """.format(identifier))
        con.commit()

    return True


def DatabaseDeleteNonDarwin():
    con = sqlite3.connect(DATABASE_PATH)
    with con:
        con.execute("""
            DELETE FROM attendees
            WHERE is_darwin = "No";
        """)
        con.commit()

    return True


def DatabaseGetSize():
    con = sqlite3.connect(DATABASE_PATH)
    with con:
        rows = con.execute("""
            SELECT * FROM attendees;
        """)
        count = 0
        for r in rows:
            count += 1
        return count

    return 0


def DatabaseClearVaccinationStatus():
    con = sqlite3.connect(DATABASE_PATH)
    with con:
        rows = con.execute("""
            UPDATE attendees
            SET pass_received = "-";
        """)
        con.commit()
    pass


def DatabaseGetVaccinationStatus(identifier):
    con = sqlite3.connect(DATABASE_PATH)
    with con:
        rows = con.execute("""
            SELECT * FROM attendees WHERE identifier = "{}";
        """.format(identifier))
        for r in rows:
            return r[5]

    return ""


def DatabaseSetVaccinated(identifier):
    # Exit if the user doesn't exist
    if DatabaseGetIndex(identifier) == -1:
        return

    con = sqlite3.connect(DATABASE_PATH)
    with con:
        con.execute("""
            UPDATE attendees
            SET pass_received = "Yes"
            WHERE identifier = "{}";
        """.format(identifier))
        con.commit()


def DatabasePrint(max_attendees, filename):
    with sqlite3.connect(DATABASE_PATH) as con, open(filename, "w") as f:

        attendees = []
        wait_list = []
        count = 1
        for row in con.execute('SELECT * FROM attendees ORDER BY number;'):
            result = []
            if count <= max_attendees:
                result.append(str(count))
                result += row[1:]
                attendees.append(result)
            else:
                result.append(str(count - max_attendees))
                result += row[1:]
                wait_list.append(result)

            count += 1

        field_names = ['Booking Order', 'Full Name', 'CRSid/Email',
                       'Wants Rueda', 'Darwin Student', 'Pass Received']

        fields = ", ".join('"' + i + '"' for i in field_names)

        print('"ATTENDEES"', file=f)
        print(fields, file=f)

        # Sort the list using the full name. Turn it into lowercase so that
        # there isn't a list of uppercase names followed by a list of lowercase
        # names.
        def take_third_lowercase(elem):
            return str(elem[1]).lower()
        sorted_attendees = sorted(attendees, key=take_third_lowercase)

        for r in sorted_attendees:
            string = ", ".join(['"{}"'.format(i) for i in r])
            print(string, file=f)

        print('""', file=f)

        print('"WAIT LIST"', file=f)
        print(fields, file=f)

        for r in wait_list:
            string = ", ".join(['"{}"'.format(i) for i in r])
            print(string, file=f)
