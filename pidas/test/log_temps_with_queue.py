import os
import sys
import subprocess
import time
import glob
from threading import Thread, RLock
from queue import Queue

devices_folder = glob.glob('/sys/bus/w1/devices/28*')


def read_temp_raw():
        catdata = subprocess.Popen(['cat', self.sensor_file], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = catdata.communicate()
        out_decode = out.decode('utf-8')
        lines = out_decode.split('\n')
        return lines

def worker():
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        print(temp_c)

