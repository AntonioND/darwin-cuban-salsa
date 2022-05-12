# SPDX-License-Identifier: Zlib
#
# Copyright (c) 2021-2022 Antonio Niño Díaz

import os
import time

from flask import Flask
from flask_bootstrap import Bootstrap

from config import Config

os.environ['TZ'] = 'Europe/London'
time.tzset()

app = Flask(__name__)
app.config.from_object(Config)

bootstrap = Bootstrap(app)

from app import routes

from app.database import *

# Initialize database if they don't exist

if not DatabaseExists():
    DatabaseReset()
