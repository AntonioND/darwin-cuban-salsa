Darwin Salsa Student Registration System
========================================

In order to run the code in this repository, you need to install the following
dependencies:

.. code:: bash

    sudo apt install python3-pip python3-dev
    pip3 install flask flask-wtf flask-bootstrap uwsgi

Note: `uwsgi` isn't needed if you just want to test the website in debug mode.
You can run the website in debug mode by running this command before starting
the server:

.. code:: bash

    export DEBUG=true

HTML server
-----------

To start the server locally just run:

.. code:: bash

    bash run.sh

Open your web browser and go to: ``http://localhost:5000``

The script ``run.sh`` is the one that defines the administrator password of the
website. Change it to something else before using it.

Contact
-------

You can contact me at antonio_nd at outlook com.

Website: http://www.skylyrac.net/

GitHub: https://github.com/AntonioND

Copyright (c) 2021-2022, Antonio Niño Díaz
