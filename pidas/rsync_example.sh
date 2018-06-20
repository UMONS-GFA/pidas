#!/usr/bin/env bash

USERNAME=''
SERVER_NAME=''
SSH_PORT=
LOCAL_FILES='/home/pi/pidas/pidas/data/data_log.*'
LOCAL_LOG_FILES='/home/pi/pidas/pidas/logs/raspardas_log.*'
REMOTE_FOLDER='/home/memoris/raw_data'
REMOTE_LOG_FOLDER='/home/memoris/logs/memoris1'
LOG_FILE_PATH='/home/pi/pidas/pidas/rsync_log'

# sync data files
/usr/bin/rsync --remove-source-files -avz -h -e  "ssh -p $SSH_PORT" $LOCAL_FILES $USERNAME@$SERVER_NAME:$REMOTE_FOLDER >> $LOG_FILE_PATH 2>&1
#sync log files
/usr/bin/rsync -avz -h -e  "ssh -p $SSH_PORT" $LOCAL_LOG_FILES $USERNAME@$SERVER_NAME:$REMOTE_LOG_FOLDER >> $LOG_FILE_PATH 2>&1

