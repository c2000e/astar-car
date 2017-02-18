#!/usr/bin/env python3
from ev3dev.ev3 import *
from time import sleep

cl = ColorSensor()
assert cl.connected, "Connect color sensor"

ts = TouchSensor()
assert ts.connected, "Connect touch sensor"

cl.mode = "COL-REFLECT"

while not ts.value():
	print(cl.value())
	sleep(1)

Sound.beep()