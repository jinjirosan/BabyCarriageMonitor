import os
import glob
import time
from ISStreamer.Streamer import Streamer

streamer = Streamer(bucket_name="Baby carriage sensors", bucket_key="Carriage_sensors", access_key="17cz22WmfeTWKu9arcQHQGcXs5Not66q")

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

base_dir_feet = '/sys/bus/w1/devices/28-031655b78bff/w1_slave'
base_dir_front = '/sys/bus/w1/devices/28-041658f324ff/w1_slave'
base_dir_headliner = '/sys/bus/w1/devices/28-041658f430ff/w1_slave'

# temperature sensor feet
def read_temp_raw_feet():
    f_feet = open(base_dir_feet, 'r')
    lines_feet = f_feet.readlines()
    f_feet.close()
    return lines_feet

def read_temp_feet():
    lines_feet = read_temp_raw_feet()
    while lines_feet[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines_feet = read_temp_raw_feet()
    equals_pos = lines_feet[1].find('t=')
    if equals_pos != -1:
        temp_string_feet = lines_feet[1][equals_pos+2:]
        temp_c_feet = float(temp_string_feet) / 1000.0
        return temp_c_feet

# temperature sensor front
def read_temp_raw_front():
    f_front = open(base_dir_front, 'r')
    lines_front = f_front.readlines()
    f_front.close()
    return lines_front

def read_temp_front():
    lines_front = read_temp_raw_front()
    while lines_front[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines_front = read_temp_raw_front()
    equals_pos = lines_front[1].find('t=')
    if equals_pos != -1:
        temp_string_front = lines_front[1][equals_pos+2:]
        temp_c_front = float(temp_string_front) / 1000.0
        return temp_c_front

# temperature sensor headliner
def read_temp_raw_headliner():
    f_headliner = open(base_dir_headliner, 'r')
    lines_headliner = f_headliner.readlines()
    f_headliner.close()
    return lines_headliner

def read_temp_headliner():
    lines_headliner = read_temp_raw_headliner()
    while lines_headliner[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines_headliner = read_temp_raw_headliner()
    equals_pos = lines_headliner[1].find('t=')
    if equals_pos != -1:
        temp_string_headliner = lines_headliner[1][equals_pos+2:]
        temp_c_headliner = float(temp_string_headliner) / 1000.0
        return temp_c_headliner

while True:
    temp_c_feet = read_temp_feet()
    temp_f_feet = temp_c_feet * 9.0 / 5.0 + 32.0
    streamer.log("feet temperature(C)", temp_c_feet)
    streamer.log("feet temperature(F)", temp_f_feet)
    time.sleep(.5)

    temp_c_front = read_temp_front()
    temp_f_front = temp_c_front * 9.0 / 5.0 + 32.0
    streamer.log("front temperature(C)", temp_c_front)
    streamer.log("front temperature(F)", temp_f_front)
    time.sleep(.5)

    temp_c_headliner = read_temp_headliner()
    temp_f_headliner = temp_c_headliner * 9.0 / 5.0 + 32.0
    streamer.log("headliner temperature(C)", temp_c_headliner)
    streamer.log("headliner temperature(F)", temp_f_headliner)
    time.sleep(.5)
