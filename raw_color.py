#!/usr/bin/env python3
from ev3dev.ev3 import *

cl = ColorSensor()
assert cl.connected, "Connect color sensor."

# Sets color sensor to return an integer value representative of the color its seeing.
cl.mode = "RGB-RAW"

while True:
	if btn.any():
		exit()
		
	else:
		print(cl.value(0), cl.value(1), cl.value(2))