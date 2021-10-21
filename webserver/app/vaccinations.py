# SPDX-License-Identifier: Zlib
#
# Copyright (c) 2021 Antonio Niño Díaz

import os

from app import app
from app.database import DatabaseSetVaccinated, DatabaseClearVaccinationStatus

FILENAME_RECORDS = "/home/" + app.config["USERNAME"] + "/vaccines.txt"


def Vaccination_Record_FileExists():
    if os.path.exists(FILENAME_RECORDS):
        return True
    return False


def Vaccination_Record_Present(identifier):
    with open(FILENAME_RECORDS, "r") as f:
        for line in f:
            if line.strip("\n") == identifier:
                return True
    return False


def Vaccination_Record_Update_Database():
    DatabaseClearVaccinationStatus()

    with open(FILENAME_RECORDS, "r") as f:
        for line in f:
            DatabaseSetVaccinated(line.strip("\n"))


def Vaccination_Record_Update(identifier_list):
    total = identifier_list

    for char in ["\r", "\n", ",", ";", ")", "("]:
        total = total.replace(char, " ")

    total = total.split()
    with open(FILENAME_RECORDS, "w") as f:
        for r in total:
            f.write("{}\n".format(r))

    Vaccination_Record_Update_Database()
