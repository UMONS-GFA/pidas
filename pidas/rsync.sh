#!/usr/bin/env bash

USERNAME=''
SERVER_NAME=''
SSH_PORT=
LOCAL_FILES='/home/pi/pidas/pidas/data/data_log.*'
REMOTE_FOLDER='/home/memoris/raw_data'
LOG_FILE_PATH='/home/pi/pidas/pidas/rsync_log'


/usr/bin/rsync --remove-source-files -avz -h -e  "ssh -p $SSH_PORT" $LOCAL_FILES $USERNAME@$SERVER_NAME:$REMOTE_FOLDER >> $LOG_FILE_PATH 2>&1

