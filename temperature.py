# simple example script to log temperatures from 3 sensors into txt file
import os
import glob
import time
import subprocess

base_dir = os.curdir
print(base_dir)
filename = 'data.txt'

base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')

def read_temp_raw(device_file):
    catdata = subprocess.Popen(['cat', device_file], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = catdata.communicate()
    out_decode = out.decode('utf-8')
    lines = out_decode.split('\n')
    return lines

def read_temp():
    temps = []
    for device in device_folder:
        device_file = device + '/w1_slave'
        lines = read_temp_raw(device_file)
        while lines[0].strip()[-3:] != 'YES':
            time.sleep(0.2)
            lines = read_temp_raw()
        equals_pos = lines[1].find('t=')
        if equals_pos != -1:
            temp_string = lines[1][equals_pos+2:]
            temp_c = float(temp_string) / 1000.0
            temps.append(temp_c)
    return temps

def save_temp():
    fd = open(filename, 'a')
    temps = read_temp()
    #cr_time = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
    cr_time = int(time.time())
    fd.write(str(cr_time) + " " + str(temps[0]) + "," + str(temps[1]) + "," + str(temps[2]) + "," + "0" '\n')
    fd.close()

if __name__ == '__main__':
    while True:
        save_temp()
        time.sleep(5)