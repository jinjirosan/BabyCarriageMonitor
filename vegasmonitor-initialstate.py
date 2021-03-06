# /usr/bin/env python
#
# Maintainer 	: JinjiroSan
# Version	: vegasmonitor 2.0 - initialstate_streamer - rewrite 3.2.3 (pep8 revision )

import os                                                      ## system terminal access
import sys                                                     ## for the exit routine
import time                                                    ## import time for sleeping
import threading                                               ## import threading
import traceback                                               ## import traceback for exception handling
import glob                                                    ## used for pathnames pattern matching
import psutil                                                  ## used for system monitoring
import dweepy                                                  ## for alerting to dweet.io
import vegasconfig                                             ## API key & secrets
from gps import *                                              ## import the gps module
from subprocess import PIPE, Popen                             ## to get the cpu temp from file
from envirophat import light, weather, motion, analog          ## the meat and potato of sensors
from ISStreamer.Streamer import Streamer                       ## getting stuff to initial state
from geopy.geocoders import Nominatim                          ## for physical address translation
from geopy.exc import GeocoderTimedOut                         ## geo error handling
from bisect import bisect_left                                 ## for chance of rain from pressure value

geolocator = Nominatim()
gpsd = gps(mode=WATCH_ENABLE)
session = gps()

## resolved --> UnicodeEncodeError: 'ascii' codec can't encode character u'\xeb' in position 16: ordinal not in range(128)
reload(sys)
sys.setdefaultencoding('utf-8')

## resolved systemd log --> stokkezero python[31114]: TERM environment variable not set.
os.environ["TERM"] = "xterm-256color"

## designate bucket name and individual access_key, dataset will append to existing bucket
streamer = Streamer(bucket_name=vegasconfig.bucket_name, bucket_key=vegasconfig.bucket_key, access_key=vegasconfig.access_key)

## modprobes for ds18b20 temp sensor
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

## ds18b20 temp sensor ID's
# base_dir_feet = '/sys/bus/w1/devices/28-031655b78bff/w1_slave'
# base_dir_front = '/sys/bus/w1/devices/28-041658f324ff/w1_slave'
base_dir_headliner = '/sys/bus/w1/devices/28-041658f014ff/w1_slave'

## KNMI historical pressure-rainchance data
raintable = {0: 80, 994: 70, 998: 60, 1002: 50, 1007: 40, 1011: 30, 1016: 20, 1020: 10}

## dweet.io parameters
thingid = 'vegasmonitor_2_0_stokke'
mydweet = {}

## function galore
def get_cpu_temperature():
    process = Popen(['vcgencmd', 'measure_temp'], stdout=PIPE)
    output, _error = process.communicate()
    return float(output[output.index('=') + 1:output.rindex("'")])

def read_enviro_temp():
    temp_raw = round(weather.temperature(), 2)
    temp_cpu = get_cpu_temperature()
    temp_calibrated = temp_raw - ((temp_cpu - temp_raw) / 0.7)     ## open air correction value 1.2 , in stokke 0.7
    return temp_calibrated

def read_enviro_heading():
    corr_heading = (motion.heading() - 10) % 360        ## verify North correction , 10 is a placeholder
    e_heading = corr_heading
    return e_heading

def read_enviro_accelerometer():
    axes = motion.accelerometer()
    return axes

def read_enviro_pressure():
    e_pressure = round(weather.pressure(), 2)
    return e_pressure * 0.01

def rainchance(pressure):
    return raintable[max({k: raintable[k] for k in raintable if k < read_enviro_pressure()})]

def read_enviro_light():
    e_light = light.light()
    return e_light

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
        temp_string_headliner = lines_headliner[1][equals_pos + 2:]
        temp_c_headliner = float(temp_string_headliner) / 1000.0
        return temp_c_headliner

##  thread to collect gpsd info
class GpsPoller(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        global gpsd                         ## bring gpsd in scope
        gpsd = gps(mode=WATCH_ENABLE)       ## start the stream of info
        self.current_value = None           ## clear
        self.running = True                 ## setting the thread running to true for the loop

    def run(self):
        global gpsd
        while gpsp.running:
            gpsd.next()

if __name__ == '__main__':
    gpsp = GpsPoller()                    ## create the thread
    try:
        gpsp.start()                      ## start and storing data in self.current_value
        mydweet = {}                      ## clear any old data in dweet.io table
        mydweet['sender'] = 'stokkezero'  ## add identifier
        while True:
            gpsd.next()
            os.system('clear')
            temp_cpu = get_cpu_temperature()
            temp_raw = round(weather.temperature(), 2)
            temp = round(read_enviro_temp(), 2)
            heading = round(read_enviro_heading(), 0)
            axes = read_enviro_accelerometer()
            pressure = round(read_enviro_pressure(), 1)
            rainchancepercentage = rainchance(pressure)
            e_light = read_enviro_light()
            temp_c_headliner = round(read_temp_headliner(), 2)
            temp_f_headliner = temp_c_headliner * 9.0 / 5.0 + 32.0
            x = round(axes[0], 1) * 100 - 40         ## correction values at the end to compensate mounting position
            y = round(axes[1], 1) * 100 + 70         ## round to one decimal place, multiply by 100 for degrees
            z = round(axes[2], 1) * 100 + 60

            ## translate the latitude and longitude into one string for the geolocator
            coordinates = str(gpsd.fix.latitude) + "," + str(gpsd.fix.longitude)

            ## Sending the data to initial state and populate dweet.io table
            streamer.log("Coordinates", coordinates)
            if coordinates == "nan,nan":        ## dweet barfs on non-existing coords, so make sure values are numerical
                mydweet['latitude'] = 0
                mydweet['longitude'] = 0
            else:
                mydweet['latitude'] = gpsd.fix.latitude
                mydweet['longitude'] = gpsd.fix.longitude
            streamer.log("Reported Time", gpsd.utc, gpsd.fix.time)
            streamer.log("Altitude (m)", gpsd.fix.altitude)
            streamer.log("Climb (m/s)", gpsd.fix.climb)
            # streamer.log("Lat Error",gpsd.fix.epy)
            # streamer.log("Long Error",gpsd.fix.epx)
            # streamer.log("Timestamp Error",gpsd.fix.ept)
            streamer.log("Speed (m/s)", gpsd.fix.speed)
            # streamer.log("Speed Error",gpsd.fix.eps)
            # streamer.log("# satellites", session.satellites)
            mydweet['number of satellites'] = session.satellites
            if gpsd.fix.mode == 1:
                streamer.log("GPS state", "no sats")
                mydweet['GPS state'] = "no sats"
            elif gpsd.fix.mode == 2:
                streamer.log("GPS state", "2D fix")
                mydweet['GPS state'] = "2D fix - no altitude"
            else:
                streamer.log("GPS state", "3D fix")
                mydweet['GPS state'] = "3D fix"
            mydweet['GPS mode'] = gpsd.fix.mode
            streamer.log("headliner temperature(C)", temp_c_headliner)
            mydweet['headliner temperature'] = temp_c_headliner
            streamer.log("headliner temperature(F)", temp_f_headliner)
            streamer.log("rpi temperature(C)", temp_cpu)
            streamer.log("enviro temperature(C) uncalibrated", temp_raw)
            streamer.log("enviro temperature(C) calibrated", temp)
            streamer.log("enviro pressure(hPa)", pressure)
            streamer.log("chance of rain(%)", rainchancepercentage)
            mydweet['rainchance'] = rainchancepercentage
            streamer.log("enviro light intensity", e_light)
            streamer.log("enviro heading", heading)
            mydweet['heading'] = heading
            streamer.log("enviro accelerometer X (roll)", x)
            mydweet['roll'] = x
            streamer.log("enviro accelerometer Y (pitch)", y)
            mydweet['pitch'] = y
            streamer.log("enviro accelerometer Z (yaw)", z)

            ## system monitoring
            disk = psutil.disk_usage('/')
            cpu_percent = psutil.cpu_percent(percpu=False)
            streamer.log("CPU Usage", cpu_percent)
            disk_percent_used = disk.percent
            streamer.log("Disk Used(%)", str("{0:.2f}".format(disk_percent_used)))
            mem = psutil.virtual_memory()
            mem_percent_used = mem.percent
            streamer.log("Memory Used(%)", str("{0:.2f}".format(mem_percent_used)))

            ## send table to dweet.io
            dweepy.dweet_for(thingid, mydweet);

            time.sleep(5)
            ## evaluate if the GPS has a fix and coords, if not the geolocator barfs so send string
            if coordinates == "nan,nan":
                noaddress = "no location data - no gps coords - probably indoors"
                streamer.log("Location", noaddress)
            elif coordinates == "0.0,0.0":
                noaddress = "no location data - no gps coords - probably indoors"
                streamer.log("Location", noaddress)
            else:
                location = geolocator.reverse(coordinates, timeout=10)  ## reverse geocode coordinates
                streamer.log("Location", location.address)
    ## if the geocoder times out, stream a message and keep looping
    except GeocoderTimedOut as e:
        streamer.log("msg", "Geocoder Timeout")
        pass

    ## user interupt or system exits by itself, print a message, close
    except (KeyboardInterrupt, SystemExit):         ## user interupt CTRL-C
        print "\nKilling Thread..."
        gpsp.running = False
        gpsp.join()                             ## wait for the thread to finish what it's doing
        print "Done.\nExiting."
