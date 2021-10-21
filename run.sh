#!/bin/bash
#
# SPDX-License-Identifier: Zlib
#
# Copyright (c) 2021 Antonio Niño Díaz

export ADMIN_PASSWORD="pass"
export DEBUG="true"

cd webserver
export FLASK_APP=webserver.py
flask run
