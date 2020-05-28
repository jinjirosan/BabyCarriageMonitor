# BabyCarriageMonitor

Sensors on the baby carriage

This is actually the second version of this project. The previous build is completed and consists of a Rpi3 with three temp sensors and the SenseHAT.

This project is trying to move to a smaller Pi Zero-W with one external temp sensor (ds18b20),the EnviroPHAT and the Adafruit Ultimate GPS v3 (using an external active GPS antenna). Possibly also integrate with the LiPo board as well for better power supply. 

The code will also livestream to an InitialState bucket instead of my own monitoring platform at home (which I'd guess not 
many 'normal' people have build in their home ...)

![dashboard example](https://github.com/jinjirosan/BabyCarriageMonitor/blob/master/images/initialstate-dashboard.png)
###### --> image: Dashboard example processing the data
![device](https://github.com/jinjirosan/BabyCarriageMonitor/blob/master/images/stokkezerobuild.jpg)
###### --> image: The device itself, with the active antenna in the back and the ds18b20 temperature sensor on the right

The following sensor inputs are used:

| Sensor                                 |  cmd  |      |
| -------------------------------------- | :---: | ---: |
| temperature (pi)                       |       |      |
| temperature (enviro)                   |       |      |
| temperature (ds18b20 sensor headliner) |       |      |
| pressure                               |       |      |
| heading (enviro motion)                |       |      |
| light (intensity, dark-bright)         |       |      |
| latitude (gps)                         |       |      |
| longitude (gps)                        |       |      |
| speed (gps)                            |       |      |
| altitude (gps)                         |       |      |
| heading (gps, north east south west)   |       |      |
| satellites (gps, #)                    |       |      |
| stance (enviro, accelerometer 3-axis)  |       |      |

In order to use the ds18b20, which connects to GPIO 4, the LEDs of the enviroPHAT are not connected (as they also use GPIO 4). So no illumination but we retain the light intensity sensor.

Power usage is 2 Watt (+/- 400 mA), Voltage is 5V, Runtime is 24 hours
C = xT
C = 0.4 * 24
C = 9.6 amp hours
Required minimal 9600 mAh to run for 24h

Muiltple files for multiple goals:
- stream to Initial State --> vegasmonitor-streamer.py-example
- stream to Cayenne --> vegasmonitor-mqtt.py-example
