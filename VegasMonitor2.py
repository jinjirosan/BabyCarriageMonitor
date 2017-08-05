#__author__ = "jinjirosan"
#__credits__ = ["", ""]
#__license__ = "GPL"
#__version__ = "2.0.1"
#__maintainer__ = "jinjirosan"
#__email__ = "<>"
#__status__ = "Test"

import os                                        ## system terminal access
from gps import *                                ## import the gps module
from time import *                               ## import time for sleeping
import threading                                 ## import threading
from sys import exit                             ## for the exit routine
import RPi.GPIO as GPIO                          ## import library to control GPIO pins
from ISStreamer.Streamer import Streamer         ## import the Initial State Streamer
from geopy.geocoders import Nominatim            ## import the Geopy geocoder
from geopy.exc import GeocoderTimedOut           ## import GeocoderTimedOut to handle Geo timeouts 
import sys, traceback                            ## import sys and traceback for exception handling
import glob                                      ## pathnames pattern matching
 
geolocator=Nominatim()                           ## call the geocoder "geolocator"
gpsd = gps(mode=WATCH_ENABLE)                    ## set gpsd to start gps info
 
#prev_input=0                                    ## set prev_input's initial value to 0, probably not really handy for streamer
 
## designate bucket name and individual access_key, dataset will append to existing bucket
streamer=Streamer(bucket_name="stokkezeroGPSDATA",bucket_key="3e198e35-2310-4fff-b740-abd98f590f5d", access_key="<access-key>")

##  Exception handling, to be worked out...
#sys.excepthook = handleTheUnhandled

## modprobes for ds18b20 temp sensor
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

## ds18b20 temp sensor ID's
#base_dir_feet = '/sys/bus/w1/devices/28-031655b78bff/w1_slave'
#base_dir_front = '/sys/bus/w1/devices/28-041658f324ff/w1_slave'
base_dir_headliner = '/sys/bus/w1/devices/28-041658f014ff/w1_slave'

## temperature sensor headliner readout and formatting
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

##  thread to collect gpsd info
class GpsPoller(threading.Thread):
 
 def __init__(self):
    threading.Thread.__init__(self)
    global gpsd 			## bring gpsd in scope
    self.current_value = None
    self.running = True 		## setting the thread running to true
 
 def run(self):
    global gpsd
    while gpsd.running:
     gpsd.next()
    sleep(10)
    
## start thread
if __name__ == '__main__':
	try:
		while True:
			gpsd.next()

			os.system('clear') ## clear the terminal window to display GPS data

			## visually make sure the script works, to be removed in production release
			print
			print ' GPS reading'
			print '----------------------------------------'
			print 'latitude ' , gpsd.fix.latitude
			print 'longitude ' , gpsd.fix.longitude
			print 'time utc ' , gpsd.utc,' + ', gpsd.fix.time
			print 'altitude (m)' , gpsd.fix.altitude
			print 'eps ' , gpsd.fix.eps
			print 'epx ' , gpsd.fix.epx
			print 'epv ' , gpsd.fix.epv
			print 'ept ' , gpsd.fix.ept
			print 'speed (m/s) ' , gpsd.fix.speed
			print 'climb ' , gpsd.fix.climb
			print 'track ' , gpsd.fix.track
			print 'mode ' , gpsd.fix.mode
			print
			print 'sats ' , gpsd.satellites

			## the geolocator requires a string so we turn lat and long into one
			coordinates = str(gpsd.fix.latitude) + "," + str(gpsd.fix.longitude)

			## stream whatever you'd like to collect from the gps
			streamer.log("Coordinates",coordinates)
			streamer.log("Reported Time",gpsd.utc,)
			streamer.log("Altitude (m)",gpsd.fix.altitude)
			streamer.log("Climb (m/s)",gpsd.fix.climb)
			streamer.log("Lat Error",gpsd.fix.epy)
			streamer.log("Long Error",gpsd.fix.epx)
			streamer.log("Timestamp Error",gpsd.fix.ept)
			streamer.log("Speed (m/s)",gpsd.fix.speed)
			streamer.log("Speed Error",gpsd.fix.eps)

			location=geolocator.reverse(coordinates,timeout=10) ## reverse geocode coordinates
			streamer.log("Location",location.address)
			
			temp_c_headliner = read_temp_headliner()
			temp_f_headliner = temp_c_headliner * 9.0 / 5.0 + 32.0
			streamer.log("headliner temperature(C)", temp_c_headliner)
			streamer.log("headliner temperature(F)", temp_f_headliner)

	## if the geocoder times out, stream a message and keep looping
	except GeocoderTimedOut as e:
		streamer.log("msg","Geocoder Timeout")
		pass

	## pressing CTRL-C or the system exits itself, print a message and close everything
	except (KeyboardInterrupt, SystemExit): 	# pressing ctrl+c
		print "\nKilling Thread..."
		streamer.close() 			# send any messages left in the streamer
		gpsd.running = False
		gpsd.join() 				# wait for the thread to finish what it's doing
		print "Done.\nExiting."
		exit() 					# exit the script
