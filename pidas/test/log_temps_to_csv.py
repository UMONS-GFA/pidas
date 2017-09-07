import sys
import subprocess
import time
import glob
import csv
import logging
import pandas as pd
from os import path, makedirs
from time import gmtime
from pidas.settings import PIDAS_DIR, SENSOR_LIST_FILE, DATA_FILE, CSV_HEADER


def get_sensor_list(sensor_list):
    """create a dataframe from sensor list name and position"""
    df = pd.read_csv(sensor_list)
    print(df)
    return df


def read_temp_raw(device_file):
    catdata = subprocess.Popen(['cat', device_file], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = catdata.communicate()
    out_decode = out.decode('utf-8')
    lines = out_decode.split('\n')
    return lines


def read_temp(device_file=''):
    lines = read_temp_raw(device_file)
    while lines[0].strip()[-3:] != 'YES':
        #time.sleep(0.2)
        lines = read_temp_raw(device_file)
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos + 2:]
        temp_c = float(temp_string) / 1000.0
        return str(temp_c)
    else:
        return None


def get_temp_measures():
    device_list = glob.glob('/sys/bus/w1/devices/28-*')

    try:
        sensors_df = get_sensor_list(path.join(PIDAS_DIR,SENSOR_LIST_FILE))
    except OSError as e:
        print(e)
        exit(1)
    temp_measures = []
    for device in device_list:
        head, sensor_id = path.split(device)
        device_file = str(device) + '/w1_slave'
        sensor_name = sensors_df['sensor_name'][sensors_df['sensor_id'] == sensor_id].values[0]
        val = read_temp(device_file)
        timestamp = str(int(time.time()))
        measure = (sensor_id, sensor_name, val, timestamp)
        temp_measures.append(measure)
    return temp_measures


if __name__ == "__main__":
    print("Begin")
    log_path = path.join(PIDAS_DIR, 'logs')
    file_path = path.join(PIDAS_DIR, DATA_FILE)
    if not path.exists(log_path):
        makedirs(log_path)
    logging_level = logging.DEBUG
    logging.Formatter.converter = gmtime
    log_format = '%(asctime)-15s %(levelname)s:%(message)s'
    logging.basicConfig(format=log_format, datefmt='%Y/%m/%d %H:%M:%S UTC', level=logging_level,
                        handlers=[logging.FileHandler(path.join(log_path,'log_temps_to_csv.log')),
                                  logging.StreamHandler()])
    logging.info('_____ Started _____')
    logging.info('saving in' + file_path)
    if not path.exists(file_path):
        with open(file_path, "w") as output_file:
            writer = csv.writer(output_file)
            writer.writerow(CSV_HEADER)
    while 1:
        try:
            temp_measures = get_temp_measures()
            for measure in temp_measures:
                with open(file_path, "a") as output_file:
                    writer = csv.writer(output_file)
                    writer.writerow(measure)
        except KeyboardInterrupt:
            print(' Exiting measures')
            sys.exit()




