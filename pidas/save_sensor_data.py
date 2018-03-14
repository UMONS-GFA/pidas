import os
import sys
import logging
from logging import handlers
import signal
import csv
from time import time, gmtime, sleep
from datetime import datetime
import requests.exceptions
from influxdb import InfluxDBClient, exceptions
from os import path, makedirs
from threading import Thread, RLock, Event

from pidas.settings import PIDAS_DIR, DATA_FILE, DATA_HEADER, DATABASE, NB_SENSOR, MEASURE_INTERVAL, SIMULATION_MODE

lock = RLock()



class customTimeRotatingFileHandler(logging.handlers.TimedRotatingFileHandler):
    def __init__(self, filename, header, when='midnight', interval=1, backupCount=0, encoding=None,
                 delay=False, utc=True, atTime=None):

        logging.handlers.TimedRotatingFileHandler.__init__(self, filename=filename, when=when,
                                                           interval=interval,
                                                  backupCount=backupCount, encoding=encoding, delay=delay,
                                                  utc=utc, atTime=atTime)
        self.file_pre_exists = os.path.exists(filename)
        self.header = header

        # Write header for first time file creation
        self.stream.write('{}\n'.format(self.header))


    def emit(self, record):
        # Call the parent class emit function.
        logging.handlers.TimedRotatingFileHandler.emit(self, record)

    def doRollover(self):
        logging.info("Rotating file...")
        logging.handlers.TimedRotatingFileHandler.doRollover(self)
        # Write header when file has rotated
        self.stream.write('{}\n'.format(self.header))


data_logger = logging.getLogger('data_logger')
data_path =  path.join(PIDAS_DIR, 'data')
if not path.exists(data_path):
    makedirs(data_path)
data_log_filename = path.join(data_path, 'data_log')
# Set data logging level and handler
data_logger.setLevel(logging.INFO)
data_handler = customTimeRotatingFileHandler(data_log_filename, header=DATA_HEADER, when='M', interval=5, delay=False)
data_handler.suffix = "%Y-%m-%d %H:%M"
data_logger.addHandler(data_handler)


if SIMULATION_MODE == 1:
    from pidas.fake_sensor import FakeTempSensor, generate_temp_sensor
else:
    from w1thermsensor import W1ThermSensor, SensorNotReadyError




def exit_threads(signum, frame):
    thread_local_save.stop()
    thread_remote_save.stop()
    logging.info("Exit({})".format(signum))
    sys.exit(signum)


class ThreadLocalSave(Thread):
    """Thread that save data locally"""
    def __init__(self, sensors, sleep_time=MEASURE_INTERVAL):
        Thread.__init__(self)
        self.sensors = sensors
        self.sleep_time = sleep_time

    def run(self):
        self.event = Event()
        logging.info("Starting {}…".format(self.getName()))
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
                            logging.error(e)
                        lock.release()
                sleep(self.sleep_time)

            finally:
                pass

    def stop(self):
        logging.info("Stopping {}…".format(self.getName()))
        self.event.set()


class ThreadRemoteSave(Thread):
    """Thread sending data to remote database"""
    def __init__(self, client, sleep_time=MEASURE_INTERVAL):
        Thread.__init__(self)
        self.client = client
        self.sleep_time = sleep_time

    def run(self):
        logging.info("Starting {}…".format(self.getName()))
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
                        logging.info("Sending data to remote database…")
                        data = []
                        for i in range(row_count):
                            time_value = datetime.utcfromtimestamp(float(new_data[i][2]))
                            value = float(new_data[i][1])
                            data.append({'measurement': 'temperatures', 'tags': {'sensorID': '%s' % new_data[i][0]},
                                         'time': time_value.strftime('%Y-%m-%d %H:%M:%S %Z'),
                                         'fields': {'value': value, 'timestamp': '%s' % new_data[i][2]}})
                        self.client.write_points(data)  # tag data with sensorID
                    except requests.exceptions.ConnectionError:
                        logging.error("Database connection lost !")

                    except exceptions.InfluxDBClientError as e:
                        logging.error("{}".format(e.content))
            except requests.exceptions.ConnectionError:
                logging.error("Database connection lost !")
            except exceptions.InfluxDBClientError as e:
                logging.error("{}".format(e.content))
            sleep(self.sleep_time)

    def stop(self):
        logging.info("Stopping {}…".format(self.getName()))
        self.event.set()


# Set the signal handler to terminate program properly
signal.signal(signal.SIGTERM, exit_threads)

log_path = path.join(PIDAS_DIR, 'logs')
file_path = path.join(PIDAS_DIR, DATA_FILE)
if not path.exists(log_path):
    makedirs(log_path)
logging_level = logging.DEBUG
logging.Formatter.converter = gmtime
log_format = '%(asctime)-15s %(levelname)s:%(message)s'
logging.basicConfig(format=log_format, datefmt='%Y/%m/%d %H:%M:%S UTC', level=logging_level,
                    handlers=[logging.FileHandler(path.join(log_path, 'save_sensor_data.log')),
                              logging.StreamHandler()])
logging.info('_____ Started _____')
logging.info('saving in' + file_path)
client = InfluxDBClient(DATABASE['HOST'], DATABASE['PORT'], DATABASE['USER'], DATABASE['PASSWORD'],
                        DATABASE['NAME'])
sensors = []
if SIMULATION_MODE == 1:
    try:
        last_timestamp = client.query('select "timestamp" from temperatures order by desc limit 1;')
        if not last_timestamp:
            logging.info("Serie is empty, creating new sensors…")
            sensors = generate_temp_sensor(NB_SENSOR)
            logging.info("Sensors generated")
        else:
            try:
                logging.info("Getting sensors from database…")
                result_set = client.query('select distinct(sensorID) as sensorID from temperatures ')
                results = list(result_set.get_points(measurement='temperatures'))
                for result in results:
                    s = FakeTempSensor()
                    s.id = result['sensorID']
                    sensors.append(s)
            except requests.exceptions.ConnectionError:
                logging.error("Database connection lost !")
    except requests.exceptions.ConnectionError:
        logging.error("Database connection lost !")
    except exceptions.InfluxDBClientError as e:
        logging.error("{}".format(e.content))
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
