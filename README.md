# pidas

[![Documentation Status](https://readthedocs.org/projects/pidas/badge/?version=latest)](http://pidas.readthedocs.io/en/latest/?badge=latest)
    
Raspberry Pi configuration to interact with Data Acquisition Systems

## Install dependencies with pipenv

    sudo pip3 install pipenv

Install from that Pipfile.lock:

    $ pipenv install --ignore-pipfile

To use it, see the [docs](http://pidas.readthedocs.io/en/latest/start.html)

Add the DATA_HEADER parameter to the settings:

    DATA_HEADER = "sensorID,value,timestamp"

Configure a cronjob for rsync script

    * * * * * /bin/bash /home/pi/pidas/pidas/rsync.sh