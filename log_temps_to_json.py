import os
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


def save_temps():
    device_list = glob.glob('/sys/bus/w1/devices/28-*')
    print(device_list)
    for device in device_list:
        temps = []
        cr_time = []
        head, sensor_id = os.path.split(device)
        device_file = str(device) + '/w1_slave'
        cr_time.append(str(int(time.time())))
        temps.append(read_temp(device_file))
        measure = TempMeasure(sensor_id, temps, cr_time)
        with open('data.json', 'a', encoding='utf-8') as f:
            json.dump(measure.to_json(), fp=f, indent=4)

if __name__ == "__main__":
    save_temps()