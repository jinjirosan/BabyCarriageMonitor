import os
import glob
import time
from ISStreamer.Streamer import Streamer
 
streamer = Streamer(bucket_name="Baby carriage sensors", bucket_key="Carriage_sensors", access_key="17cz22WmfeTWKu9arcQHQGcXs5Not66q")
 
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')
 
base_dir_feet = '/sys/bus/w1/devices/28-031655b78bff/w1_slave'
base_dir_front = '/sys/bus/w1/devices/28-031655b78bff/w1_slave'
base_dir_headliner = '/sys/bus/w1/devices/28-031655b78bff/w1_slave'

# temperature sensor feet
def read_temp_raw_feet():
    f = open(base_dir_feet, 'r')
    lines_feet = f.readlines()
    f.close()
    return lines
 
def read_temp_feet():
    lines_feet = read_temp_raw_feet()
    while lines_feet[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines_feet = read_temp_raw_feet()
    equals_pos = lines_feet[1].find('t=')
    if equals_pos != -1:
        temp_string_feet = lines_feet[1][equals_pos+2:]
        temp_c_feet = float(temp_string) / 1000.0
        return temp_c_feet
 
while True:
    temp_c_feet = read_temp_feet()
    temp_f_feet = temp_c_feet * 9.0 / 5.0 + 32.0
    streamer.log("feet temperature(C)", temp_c_feet)
    streamer.log("feet temperature(F)", temp_f_feet)
    time.sleep(.5)

## 
