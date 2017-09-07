import sys
import subprocess
import time
import glob
import csv
import logging
import pandas as pd
from os import path, makedirs
from time import gmtime
from w1thermsensor import W1ThermSensor
from pidas.settings import PIDAS_DIR, SENSOR_LIST_FILE, DATA_FILE

def get_sensor_list(sensor_list):
    """create a dataframe from sensor list name and position"""
    df = pd.read_csv(sensor_list)
    return df

def read_temps():
    temp_measures = []
    for sensor in W1ThermSensor.get_available_sensors():
        sensor = W1ThermSensor(W1ThermSensor.THERM_SENSOR_DS18B20, device_file)
        temperature_in_celsius = sensor.get_temperature()
        print(temperature_in_celsius)
        #return temperature_in_celsius

if __name__ == "__main__":
    read_temps()