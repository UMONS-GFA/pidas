# script to log temperatures from sensors into a DTM file
import os
import sys
import glob
import time
import subprocess


devices_folder = glob.glob('/sys/bus/w1/devices/28*')


def initialize_dtm(file):
    with open(file, 'w', encoding='utf-8') as f:
        f.write("# DATE: " + str(time.strftime("%Y-%m-%d", time.gmtime())) + "\n")
        f.write("# PROG: " + sys.argv[0] + "\n")
        f.write("# SITE: " + "\n")
        f.write("# UDAS: " + "\n")
        f.write("# TITL: " + "\n")
        f.write("# CHAN: " + "YYYY MM DD HH NN SS 0001_() 0002_() 0003_() 0004_()" + "\n")


def read_temp_raw(device_file):
    catdata = subprocess.Popen(['cat', device_file], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = catdata.communicate()
    out_decode = out.decode('utf-8')
    lines = out_decode.split('\n')
    return lines


def read_temp():
    temps = []
    for device in devices_folder:
        device_file = device + '/w1_slave'
        lines = read_temp_raw(device_file)
        while lines[0].strip()[-3:] != 'YES':
            time.sleep(0.2)
            lines = read_temp_raw(device_file)
        equals_pos = lines[1].find('t=')
        if equals_pos != -1:
            temp_string = lines[1][equals_pos+2:]
            temp_c = float(temp_string) / 1000.0
            temps.append(temp_c)
    return temps


def save_temp(file):
    fd = open(file, 'a')
    temps = read_temp()
    #cr_time = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
    cr_time = int(time.time())
    fd.write(str(cr_time) + " ")
    for temp in temps:
        fd.write(str(temp) + " ")
    fd.write('\n')
    fd.close()


if __name__ == '__main__':
    base_dir = os.curdir
    filename = str(time.strftime("%Y-%m-%d", time.gmtime()) + ".DTM")
    if not os.path.isfile(base_dir + "/" + filename):
        initialize_dtm(filename)
    try:
        while True:
            print(read_temp())
            save_temp(filename)
            time.sleep(1)
    except KeyboardInterrupt:
        print(' Exiting measures')
        sys.exit()
