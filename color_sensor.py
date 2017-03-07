#!/usr/bin/env python3
from ev3dev.ev3 import *
from time import sleep
from math import sqrt

UNKNOWN = 0
BLACK = 1
WHITE = 2
RED = 3



cl = ColorSensor()
assert cl.connected, "Connect color sensor."

cl.mode = "RGB-RAW"

past_readings = []

current_color = UNKNOWN

while True:
	red = cl.value(0)
	green = cl.value(1)
	blue = cl.value(2)
	
	average = (red + green + blue)/3

	red_diff = (red - average) * (red - average)
	green_diff = (green - average) * (green - average)
	blue_diff = (blue - average) * (blue - average)
	
	square_diff_avg = (red_diff + green_diff + blue_diff)/3

	st_dev = sqrt(square_diff_avg)

	if st_dev > 0 and st_dev < 10:
		if red < 45 and green < 45 and blue < 45:
			current_color = BLACK
	
	elif st_dev > 25 and st_dev < 35:
		if red > 210 and green > 240 and blue > 180:
			current_color = WHITE

	elif st_dev > 70 and st_dev < 90:
		if red > 180 and green > 40 and blue > 20:
			current_color = RED

	else:
		current_color = UNKNOWN


	if len(past_readings) < 10:
		past_readings.append(current_color)
		
	else:
		for i in range(9):
			past_readings[i] = past_readings[i + 1]

		past_readings[9] = current_color		


	print(red, green, blue, st_dev)
	print(past_readings)
	sleep(1)
