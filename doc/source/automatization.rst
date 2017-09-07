Automatization
==============

Edit your cron file::

    crontab -e

Add your PYTHONPATH at the beginning of the file

    PYTHONPATH=/home/USERNAME/pidas

And add a command to launch the script at boot::

    @reboot /usr/bin/python3 /home/USERNAME/pidas/pidas/save_sensor_data.py >> /home/USERNAME/pidas/pidas/cronlog 2>&1

