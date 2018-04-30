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
    
Make a copy of **rsync_example.sh** as **rsync.sh** and configure it to meet your needs

    USERNAME=''
    SERVER_NAME=''
    SSH_PORT=
    LOCAL_FILES='/home/pi/pidas/pidas/data/data_log.*'
    REMOTE_FOLDER='/home/memoris/raw_data'
    LOG_FILE_PATH='/home/pi/pidas/pidas/rsync_log'

Configure a cronjob for rsync script

    * * * * * /bin/bash /home/pi/pidas/pidas/rsync.sh
    
Set a static ip(optional)

On Debian 9 (stretch) edit **/etc/dhcpcd.conf**

    interface eth0
    static ip_address=192.168.0.10/24
    static ip6_address=fd51:42f8:caae:d92e::ff/64
    static routers=192.168.0.1
    static domain_name_servers=192.168.0.1 8.8.8.8 fd51:42f8:caae:d92e::1
