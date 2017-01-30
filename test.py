#!/usr/bin/env python3
from ev3dev.ev3 import *
import time
import random

ir = InfraredSensor()
assert ir.connected, "Connect ultrasound sensor"
ir.mode = "IR-PROX"

gy = GyroSensor()
assert gy.connected, "Connect gyro sensor"
gy.mode = "GYRO-RATE"
gy.mode = "GYRO-ANG"

motors = [LargeMotor(address) for address in (OUTPUT_B, OUTPUT_C)]
assert all([m.connected for m in motors]), "Connect motors to B & C"

base_speed = -540

def run():
	for m in motors:
		m.run_forever()

def correct():
	angle = gy.value()
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

Sound.tone([(1500, 500, 100), (1000, 500)]).wait()

distance = ir.value()
heading = 0
j = 0
while True:
	while distance > 50:			
		correct()
		run()

		distance = ir.value()

	for m in motors:
		m.stop(stop_action = "hold")

	Sound.tone(1500, 1000).wait()

	time.sleep(3)

	distance = ir.value()

	if distance < 50:
		Sound.tone(1500, 1000).wait()

		direction = random.choice(-1,1)

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

	Sound.tone(1000, 1000).wait()