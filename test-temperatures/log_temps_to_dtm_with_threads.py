import os
import sys
import subprocess
import time
import glob
from threading import Thread, RLock
from queue import Queue

verrou = RLock()

devices_folder = glob.glob('/sys/bus/w1/devices/28*')


class Temperature(Thread):

    def __init__(self, sensor_file):
        Thread.__init__(self)
        self.sensor_file = sensor_file

    def read_temp_raw(self):
        catdata = subprocess.Popen(['cat', self.sensor_file], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = catdata.communicate()
        out_decode = out.decode('utf-8')
        lines = out_decode.split('\n')
        return lines

    def run(self):
        lines = self.read_temp_raw()
        while lines[0].strip()[-3:] != 'YES':
            time.sleep(0.2)
            lines = self.read_temp_raw()
        equals_pos = lines[1].find('t=')
        if equals_pos != -1:
            temp_string = lines[1][equals_pos+2:]
            temp_c = float(temp_string) / 1000.0
            print(temp_c)


if __name__ == '__main__':
    base_dir = os.curdir
    try:
        start = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
        print(start)
        # for device in devices_folder:
        #     device_file = device + '/w1_slave'
        #     thread = Temperature(device_file)
        #     thread.start()
        #     thread.join()
        # device_file0 = devices_folder[0] + '/w1_slave'
        # thread0 = Temperature(device_file0)
        # device_file1 = devices_folder[1] + '/w1_slave'
        # thread1 = Temperature(device_file1)
        # device_file2 = devices_folder[2] + '/w1_slave'
        # thread2 = Temperature(device_file2)
        #
        # thread0.start()
        # thread1.start()
        # thread2.start()
        #
        # thread0.join()
        # thread1.join()
        # thread2.join()

        q = Queue()
        for device in devices_folder:
            device_file = device + '/w1_slave'
            t = Temperature(device_file)
            t.daemon = True
            t.start()

        q.join()

        #time.sleep(1)
        stop = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
        print(stop)
    except KeyboardInterrupt:
        print(' Exiting measures')
        sys.exit()
