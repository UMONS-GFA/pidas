import os
import sys
import subprocess
import time
import glob
import json

from Measure import TempMeasure


def read_temp_raw(device_file):
    catdata = subprocess.Popen(['cat', device_file], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = catdata.communicate()
    out_decode = out.decode('utf-8')
    lines = out_decode.split('\n')
    return lines


def read_temp(device_file=''):
    lines = read_temp_raw(device_file)
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
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
    temp_measures = []
    for device in device_list:
        temps = []
        cr_time = []
        head, sensor_id = os.path.split(device)
        device_file = str(device) + '/w1_slave'
        cr_time.append(str(int(time.time())))
        temps.append(read_temp(device_file))
        temp_measure = TempMeasure(sensor_id, temps, cr_time)
        temp_measures.append(temp_measure.to_json())
    return temp_measures


def save_to_json(temps):
    with open('data.json', 'a', encoding='utf-8') as f:
        #f.write(json.dumps(temps, indent=4))
        f.write(json.dumps(temps))

if __name__ == "__main__":
    while 1:
        try:
            temp_measures = get_temp_measures()
            save_to_json(temp_measures)
            time.sleep(60)
        except KeyboardInterrupt:
            print(' Exiting measures')
            sys.exit()
