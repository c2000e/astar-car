#!/usr/bin/env python3
from ev3dev.ev3 import *
from time import sleep

cl = ColorSensor()
assert cl.connected, "Connect color sensor"

ts = TouchSensor()
assert ts.connected, "Connect touch sensor"

cl.mode = "COL-COLOR"

colors = ("unknown", "black", "blue", "green", "yellow", "red", "white", "brown")

while not ts.value():
	print(colors[cl.value()])
	sleep(1)

Sound.beep()