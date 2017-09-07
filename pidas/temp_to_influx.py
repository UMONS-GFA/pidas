import datetime
import pandas as pd
from influxdb import DataFrameClient, InfluxDBClient
from w1thermsensor import W1ThermSensor
from pidas.settings import DATABASE


client = DataFrameClient(DATABASE['HOST'], DATABASE['PORT'], DATABASE['USER'], DATABASE['PASSWORD'], DATABASE['NAME'])

while 1:
    for sensor in W1ThermSensor.get_available_sensors():
        print("Sensor %s has temperature %.2f" % (sensor.id, sensor.get_temperature()))