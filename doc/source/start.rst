Getting started
===============

Get the code::

    git clone https://github.com/UMONS-GFA/pidas.git

Create a **settings.py** file in the pidas/pidas directory.
Your can now configure your custom settings.

``DATABASE``
------------

InfluxDB is used. This can be configured using the following::

    DATABASE = {
        'HOST': '127.0.0.1',
        'PORT': 8086,
        'USER': 'mydatabaseuser',
        'PASSWORD': 'mypassword',
        'NAME': 'mydatabase'
    }

``CSV_HEADER``
--------------

Your CSV file header::

    CSV_HEADER = ["sensorID", "sensorName", "value", "timestamp"]

``PIDAS_DIR``
-------------

The absolute path to the project::

    PIDAS_DIR = '/home/USERNAME/pidas'

``DATA_FILE``
-------------

File where your date will be saved::

    DATA_FILE = 'data.csv'

``LOG_DIR``
-----------

The relative path directory to your logs::

    LOG_DIR = 'logs/'

``NB_SENSOR``
-------------

Number of sensors you want to generate::

    NB_SENSOR = 8

``SIMULATION_MODE``
-------------------

If simulation mode is set to 1, sensors will be created::

   SIMULATION_MODE = 0



