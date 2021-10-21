# SPDX-License-Identifier: Zlib
#
# Copyright (c) 2021 Antonio Niño Díaz

import os

class Config(object):
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD')
    USERNAME = os.environ.get('USER')

    # This key is needed so that Flask-WTF input forms work
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'darwin-salsa-secret'
