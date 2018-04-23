import os
import sys
import logging
import signal
import csv
from time import time, gmtime, sleep
from datetime import datetime
import requests.exceptions
from influxdb import InfluxDBClient, exceptions
from os import path, makedirs
from threading import Thread, RLock, Event

from pidas.settings import PIDAS_DIR, DATA_FILE, DATA_HEADER, DATABASE, NB_SENSOR, MEASURE_INTERVAL, SIMULATION_MODE
from pidas.custom_file_handler import CustomTimeRotatingFileHandler

lock = RLock()

# TODO: fix logging
# TODO: change filenames
# TODO: choose message debug level



# Debug logger setup
msg_logger = logging.getLogger('msg_logger')
log_path = path.join(PIDAS_DIR, 'logs')
file_path = path.join(PIDAS_DIR, DATA_FILE)
if not path.exists(log_path):
    makedirs(log_path)
msg_log_filename = path.join(log_path, 'save_sensor_data.log')

# set message loggin level and handler
log_format = '%(asctime)-15s | %(process)d | %(levelname)s: %(message)s'
msg_logger.setLevel(logging.DEBUG)
msg_handler = CustomTimeRotatingFileHandler(msg_log_filename, header='')
msg_formatter = logging.Formatter(log_format)
msg_formatter.converter = gmtime
msg_formatter.datefmt = '%Y/%m/%d %H:%M:%S UTC'
msg_logger.addHandler(msg_handler)




# Data logger setup
data_logger = logging.getLogger('data_logger')
data_path =  path.join(PIDAS_DIR, 'data')
if not path.exists(data_path):
    makedirs(data_path)
data_log_filename = path.join(data_path, 'data_log')
# Set data logging level and handler
data_logger.setLevel(logging.INFO)
data_handler = CustomTimeRotatingFileHandler(data_log_filename, header=DATA_HEADER)
data_handler.suffix = "%Y_%m_%d_%H_%M"
data_logger.addHandler(data_handler)


if SIMULATION_MODE == 1:
    from pidas.fake_sensor import FakeTempSensor, generate_temp_sensor
else:
    from w1thermsensor import W1ThermSensor, SensorNotReadyError




def exit_threads(signum, frame):
    thread_local_save.stop()
    thread_remote_save.stop()
    msg_logger.info("Exit({})".format(signum))
    sys.exit(signum)


class ThreadLocalSave(Thread):
    """Thread that save data locally"""
    def __init__(self, sensors, sleep_time=MEASURE_INTERVAL):
        Thread.__init__(self)
        self.sensors = sensors
        self.sleep_time = sleep_time

    def run(self):
        self.event = Event()
        msg_logger.info("Starting {}…".format(self.getName()))
        while not self.event.isSet():
            try:
                if SIMULATION_MODE == 1:
                    for sensor in self.sensors:
                        timestamp = int(time())
                        lock.acquire()
                        temperature = sensor.get_temperature()
                        row = "{},{},{}".format(sensor.id, temperature, timestamp)
                        data_logger.info(row)
                        lock.release()
                else:
                    for sensor in W1ThermSensor.get_available_sensors():
                        # TODO: set a sensor name
                        timestamp = int(time())
                        lock.acquire()
                        try:
                            temperature = sensor.get_temperature()
                            row = "{},{},{}".format(sensor.id, temperature, timestamp)
                            data_logger.info(row)
                        except SensorNotReadyError as e:
                            msg_logger.error(e)
                        lock.release()
                sleep(self.sleep_time)

            finally:
                pass

    def stop(self):
        msg_logger.info("Stopping {}…".format(self.getName()))
        self.event.set()


class ThreadRemoteSave(Thread):
    """Thread sending data to remote database"""
    def __init__(self, client, sleep_time=MEASURE_INTERVAL):
        Thread.__init__(self)
        self.client = client
        self.sleep_time = sleep_time

    def run(self):
        msg_logger.info("Starting {}…".format(self.getName()))
        self.event = Event()
        while not self.event.isSet():
            try:
                result_set = self.client.query('select "timestamp" from temperatures order by desc limit 1;')
                results = list(result_set.get_points(measurement='temperatures'))
                if not results:
                    last_timestamp = datetime.utcfromtimestamp(0)
                else:
                    last_timestamp = float(results[0]['timestamp'])
                    last_timestamp = datetime.utcfromtimestamp(last_timestamp)
                new_data = []
                lock.acquire()

                with open(data_log_filename, newline='') as csvfile:
                    csv_data = csv.reader(csvfile, delimiter=',')
                    header = csv_data.__next__()
                    for row in csv_data:

                        row_date = datetime.utcfromtimestamp(int(row[2]))
                        if  row_date > last_timestamp:
                            new_data.append(row)
                lock.release()
                row_count = len(new_data)
                if row_count > 0:
                    try:
                        msg_logger.info("Sending data to remote database…")
                        data = []
                        for i in range(row_count):
                            time_value = datetime.utcfromtimestamp(float(new_data[i][2]))
                            value = float(new_data[i][1])
                            data.append({'measurement': 'temperatures', 'tags': {'sensorID': '%s' % new_data[i][0]},
                                         'time': time_value.strftime('%Y-%m-%d %H:%M:%S %Z'),
                                         'fields': {'value': value, 'timestamp': '%s' % new_data[i][2]}})
                        self.client.write_points(data)  # tag data with sensorID
                    except requests.exceptions.ConnectionError:
                        msg_logger.error("Database connection lost !")

                    except exceptions.InfluxDBClientError as e:
                        msg_logger.error("{}".format(e.content))
            except requests.exceptions.ConnectionError:
                msg_logger.error("Database connection lost !")
            except exceptions.InfluxDBClientError as e:
                msg_logger.error("{}".format(e.content))
            sleep(self.sleep_time)

    def stop(self):
        msg_logger.info("Stopping {}…".format(self.getName()))
        self.event.set()


# Set the signal handler to terminate program properly
signal.signal(signal.SIGTERM, exit_threads)



msg_logger.info('_____ Started _____')
msg_logger.info('saving in' + data_log_filename)
client = InfluxDBClient(DATABASE['HOST'], DATABASE['PORT'], DATABASE['USER'], DATABASE['PASSWORD'],
                        DATABASE['NAME'])
sensors = []
if SIMULATION_MODE == 1:
    try:
        last_timestamp = client.query('select "timestamp" from temperatures order by desc limit 1;')
        if not last_timestamp:
            msg_logger.info("Serie is empty, creating new sensors…")
            sensors = generate_temp_sensor(NB_SENSOR)
            msg_logger.info("Sensors generated")
        else:
            try:
                msg_logger.info("Getting sensors from database…")
                result_set = client.query('select distinct(sensorID) as sensorID from temperatures; ')
                results = list(result_set.get_points(measurement='temperatures'))
                for result in results:
                    s = FakeTempSensor()
                    s.id = result['sensorID']
                    sensors.append(s)
            except requests.exceptions.ConnectionError:
                msg_logger.error("Database connection lost !")
    except requests.exceptions.ConnectionError:
        msg_logger.error("Database connection lost !")
    except exceptions.InfluxDBClientError as e:
        msg_logger.error("{}".format(e.content))
else:
    sensors = W1ThermSensor.get_available_sensors()
thread_local_save = ThreadLocalSave(sensors=sensors)
thread_local_save.setName('localSavingThread')
thread_remote_save = ThreadRemoteSave(client)
thread_remote_save.setName('remoteSavingThread')
thread_local_save.start()
thread_remote_save.start()
# wait until threads terminates before stopping main
thread_local_save.join()
thread_remote_save.join()
