# BabyCarriageMonitor
Sensors on the baby carriage

This is actually the second version of this project. The previous build is completed and consists of a Rpi3 with three temp sensors and the SenseHAT.

This project is trying to move to a smaller Pi Zero-W with one external temp sensor (ds18b20),the EnviroPHAT and the Adafruit Ultimate GPS v3. Possibly also integrate with the LiPo board as well for better power supply. 

The code will also livestream to an InitialState bucket instead of my own monitoring platform at home (which I'd guess not many 'normal' people have build in their home ...)

The following sensor inputs are used:

| Sensor        | cmd           |  |
| ------------- |:-------------:| -----:|
| temperature (pi)     | tempenviro = round(weather.temperature(),2) |  |
| temperature (enviro)     | centered      |   |
| temperature (ds18 sensor headliner)	 | are neat      |    |
| pressure | pressureenviro = round(weather.pressure(),2)      |   |
| heading (enviro motion) | headingenviro = motion.heading()      |   |
| light (intensity, dark-bright) | lightenviro = light.light()      |  |
| latitude (gps) |       |    |
| longitude (gps) |       |   |
| speed (gps) | are neat      |    |
| altitude (gps) | are neat      |    |
| heading (gps, north east south west) |       |    |
| satellites (gps, #) |      |    |
| stance (enviro, accelerometer 3-axis)	 |       |  |

