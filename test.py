#!/usr/bin/env python3
from ev3dev.ev3 import *
import time
import random

Leds.all_off()

ir = InfraredSensor()
assert ir.connected, "Connect ultrasound sensor"
ir.mode = "IR-PROX"

gy = GyroSensor()
assert gy.connected, "Connect gyro sensor"
gy.mode = "GYRO-RATE"
gy.mode = "GYRO-ANG"

motors = [LargeMotor(address) for address in (OUTPUT_B, OUTPUT_C)]
assert all([m.connected for m in motors]), "Connect motors to B & C"

lcd = Screen()

smile = True
base_speed = -540
min_distance = 70
random = True

def run():
	for m in motors:
		m.run_forever()

def correct():
	angle = gy.value()
	
	while raw_angle > 360:
		raw_angle -= 360

	error = heading - angle 
	percent_error = error/25

	if percent_error < (900/base_speed) + 1:
		percent_error = (900/base_speed) + 1

	elif percent_error > (-900/base_speed) - 1:
		percent_error = (-900/base_speed) - 1

	i = 0
	for m in motors:
		if i == 0:
			m.speed_sp = base_speed - (base_speed * percent_error)
		else:
			m.speed_sp = base_speed + (base_speed * percent_error)
		i += 1

def turn():
	angle = gy.value()
	
	if angle < heading:
		i = 0
		for m in motors:
			if i == 0:
				m.speed_sp = -base_speed/3
			else:
				m.speed_sp = base_speed/3
	
			i += 1

	if angle > heading:
		i = 0
		for m in motors:
			if i == 0:
				m.speed_sp = base_speed/3
			else:
				m.speed_sp = -base_speed/3
			i += 1

def draw(smile):
	lcd.clear()

	lcd.draw.ellipse((20, 20, 60, 60))
	lcd.draw.ellipse((118, 20, 158, 60))

	if smile:
		lcd.draw.arc((20, 80, 158, 100), 0, 180)
	
	else:
		lcd.draw.arc((20, 80, 158, 100), 0, 180)

Sound.tone([(1500, 500, 100), (1000, 500)]).wait()

distance = ir.value()
heading = 0
j = 0
while True:
	while distance > min_distance:
		correct()
		run()

		distance = ir.value()

		smile = True
		draw(smile)

	for m in motors:
		m.stop(stop_action = "hold")

	smile = False
	draw(smile)

	Leds.set_color(Leds.LEFT, Leds.RED)
	Leds.set_color(Leds.RIGHT, Leds.RED)

	Sound.tone(1500, 1000).wait()

	time.sleep(3)

	distance = ir.value()

	if distance < min_distance:

		Sound.tone(1500, 1000).wait()

		if random == True:
			direction = random.choice((-1,1))
		else:
			direction = 1

		heading = 88 * direction
		angle = gy.value()

		while heading != angle:
			angle = gy.value()
			turn()
			run()

		for m in motors:
			m.stop(stop_action = "hold")
		
		gy.mode = "GYRO-RATE"
		gy.mode = "GYRO-ANG"
		
		heading = 0
		
		time.sleep(3)		

		distance = ir.value()
		j += 1

	Leds.set_color(Leds.LEFT, Leds.GREEN)
	Leds.set_color(Leds.RIGHT, Leds.GREEN)
		
	Sound.tone(1000, 1000).wait()