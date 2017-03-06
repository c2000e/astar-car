#!/usr/bin/env python3
from ev3dev.ev3 import *
from time import sleep

cl = ColorSensor()
assert cl.connected, "Connect color sensor."

cl.mode = "RGB.RAW"

while True:
	print(cl.value(0), cl.value(1), cl.value(2))
	sleep(1)