import time
import datetime
import logging
import csv
from pandas import read_csv, to_datetime
from influxdb import DataFrameClient
from os import path, makedirs
from threading import Thread, RLock

from pidas.settings import PIDAS_DIR, DATA_FILE, CSV_HEADER, DATABASE

lock = RLock()


SIMULATION_MODE = 0

if SIMULATION_MODE == 1:
    from pidas.fake_sensor import FakeTempSensor
else:
    from w1thermsensor import W1ThermSensor


class ThreadLocalSave(Thread):
    """Thread that save data locally"""
    def __init__(self, file_path, sensors, sleep_time=2):
        Thread.__init__(self)
        self.csv_path = file_path
        self.sensors = sensors
        self.sleep_time = sleep_time

    def run(self):
        while 1:
            try:
                if SIMULATION_MODE == 1:
                    for sensor in self.sensors:
                        timestamp = str(int(time.time()))
                        lock.acquire()
                        with open(self.csv_path, "a") as output_file:
                            writer = csv.writer(output_file)
                            row = sensor.id, sensor.name, sensor.get_temperature(), timestamp
                            writer.writerow(row)
                            lock.release()
                else:
                    for sensor in W1ThermSensor.get_available_sensors():
                        # TODO: set a sensor name
                        timestamp = str(int(time.time()))
                        lock.acquire()
                        with open(self.csv_path, "a") as output_file:
                            writer = csv.writer(output_file)
                            row = sensor.id, 'T', sensor.get_temperature(), timestamp
                            writer.writerow(row)
                            lock.release()
                time.sleep(self.sleep_time)

            finally:
                pass


class ThreadRemoteSave(Thread):
    """Thread sending data to remote database"""
    def __init__(self, client, file_path, sleep_time=10):
        Thread.__init__(self)
        self.client = client
        self.csv_path = file_path
        self.sleep_time = sleep_time

    def run(self):

        while 1:
            lock.acquire()
            df = read_csv(self.csv_path)
            df['valueTime'] = to_datetime(df['timestamp'], utc=True)
            df.set_index(['valueTime'], inplace=True)
            lock.release()
            last_measurement = self.client.query('select * from temperatures order by desc limit 1;')
            if not last_measurement:
                last_date = datetime.datetime(1970, 1, 1, 0, 0, 0).replace(tzinfo=datetime.timezone.utc)
            else:
                last_date = last_measurement["temperatures"].index.to_pydatetime()[0]
            df2 = df[df.index > last_date]
            if df2.size > 0:
                logging.info("Sending data to remote database…")
                for sensorName in df2['sensorName'].unique():
                    sensor_data = df2.query("sensorName=='" + sensorName + "'")  # df data for one sensor
                    self.client.write_points(sensor_data, 'temperatures', {'sensorName': sensorName})  # tag data with sensorID
                time.sleep(self.sleep_time)


def generate_temp_sensor(nb_sensor=7):
    sensors = []
    logging.info("Generating sensors")
    for i in range(nb_sensor):
        s = FakeTempSensor()
        s.set_name('T' + str(i))
        sensors.append(s)
        time.sleep(1)  # mandatory otherwise each sensor will have the same name
        logging.info(".")
    logging.info("Sensors generated")
    return sensors


def main():
    log_path = path.join(PIDAS_DIR, 'logs')
    file_path = path.join(PIDAS_DIR, DATA_FILE)
    if not path.exists(log_path):
        makedirs(log_path)
    logging_level = logging.DEBUG
    logging.Formatter.converter = time.gmtime
    log_format = '%(asctime)-15s %(levelname)s:%(message)s'
    logging.basicConfig(format=log_format, datefmt='%Y/%m/%d %H:%M:%S UTC', level=logging_level,
                        handlers=[logging.FileHandler(path.join(log_path, 'log_temps_to_csv2.log')),
                                  logging.StreamHandler()])
    logging.info('_____ Started _____')
    logging.info('saving in' + file_path)
    if not path.exists(file_path):
        with open(file_path, "w") as output_file:
            writer = csv.writer(output_file)
            writer.writerow(CSV_HEADER)
    client = DataFrameClient(DATABASE['HOST'], DATABASE['PORT'], DATABASE['USER'], DATABASE['PASSWORD'],
                             DATABASE['NAME'])
    if SIMULATION_MODE == 1:
        last_measurement = client.query('select * from temperatures order by desc limit 1;')
        if not last_measurement:
            "Serie is empty, creating new sensors…"
            sensors = generate_temp_sensor()
        else:
            "Getting sensors from database…"
            result_set = client.query('select distinct(sensorID) as sensorID from temperatures ')
            sensors = []
            for result in result_set['temperatures'].sensorID:
                s = FakeTempSensor()
                s.id = result
                sensors.append(s)
    else:
        sensors = W1ThermSensor.get_available_sensors()

    thread_local_save = ThreadLocalSave(file_path=file_path, sensors=sensors)
    thread_remote_save = ThreadRemoteSave(client, file_path=file_path)
    thread_local_save.start()
    thread_remote_save.start()


if __name__ == "__main__":
    main()
