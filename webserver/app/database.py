# SPDX-License-Identifier: Zlib
#
# Copyright (c) 2021-2022 Antonio Niño Díaz

import base64
import sqlite3
import os

from app import app

#import time

DATABASE_PATH = "/home/" + app.config["USERNAME"] + "/attendees.db"


def EncodeBase64(string):
    string_bytes = string.encode('UTF-8')
    base64_string_bytes = base64.b64encode(string_bytes)
    base64_string = base64_string_bytes.decode('UTF-8')
    return base64_string


def DecodeBase64(base64_string):
    base64_string_bytes = base64_string.encode('UTF-8')
    string_bytes = base64.b64decode(base64_string_bytes)
    string = string_bytes.decode('UTF-8')
    return string


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
                is_darwin STRING
            );
        """)
        con.commit()


def DatabaseAdd(full_name, identifier, is_darwin):
    # Don't allow multiple registrations by the same user
    if DatabaseGetIndex(identifier) != -1:
        return False

    full_name_base64 = EncodeBase64(full_name)
    identifier_base64 = EncodeBase64(identifier)

    con = sqlite3.connect(DATABASE_PATH)
    with con:
        con.execute("""
            INSERT INTO attendees (name, identifier, is_darwin)
            VALUES ('{}','{}','{}');
        """.format(full_name_base64, identifier_base64, is_darwin))
        con.commit()
        #time.sleep(20)

    return True


def DatabaseGetIndex(identifier):
    identifier_base64 = EncodeBase64(identifier)

    con = sqlite3.connect(DATABASE_PATH)
    with con:
        rows = con.execute("""
            SELECT * FROM attendees;
        """)
        count = 1
        for r in rows:
            if r[2] == identifier_base64:
                return count
            count += 1
    return -1


def DatabaseDelete(identifier):
    # Fail if the user doesn't exist
    if DatabaseGetIndex(identifier) == -1:
        return False

    identifier_base64 = EncodeBase64(identifier)

    con = sqlite3.connect(DATABASE_PATH)
    with con:
        con.execute("""
            DELETE FROM attendees
            WHERE identifier = "{}";
        """.format(identifier_base64))
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


def DatabasePrint(max_attendees, filename):
    with sqlite3.connect(DATABASE_PATH) as con, open(filename, "w") as f:

        attendees = []
        wait_list = []
        count = 1
        for row in con.execute('SELECT * FROM attendees ORDER BY number;'):
            result = []
            if count <= max_attendees:
                result.append(str(count))
                result.append(DecodeBase64(row[1]))
                result.append(DecodeBase64(row[2]))
                result.extend(row[3:])
                attendees.append(result)
            else:
                result.append(str(count - max_attendees))
                result.append(DecodeBase64(row[1]))
                result.append(DecodeBase64(row[2]))
                result.extend(row[3:])
                wait_list.append(result)

            count += 1

        field_names = ['Booking Order', 'Full Name', 'CRSid/Email',
                       'Darwin Student']

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
