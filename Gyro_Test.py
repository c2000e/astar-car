#!/usr/bin/env python3
from ev3dev.ev3 import *
import time
import random

#
ir = InfraredSensor()
gy = GyroSensor()
l_motor = LargeMotor(OUTPUT_B)
r_motor = LargeMotor(OUTPUT_C)
LCD_screen = Screen()

#Checks that all devices are connected to the ev3.
assert ir.connected, "Connect ultrasound sensor"
assert gy.connected, "Connect gyro sensor"
assert l_motor.connected, "Connect motor to B"
assert r_motor.connected, "Connect motor to C"

#
ir.mode = "IR-PROX"

#
base_speed = -540
#
max_speed = -900
#
turn_speed_reduction = 0.05

#
distance = ir.value()
#
min_distance = 70

#
heading = 0

#
random = False
#
canSee = True

#
def run_motors():
	l_motor.run_forever()
	r_motor.run_forever()

#
def stop_motors():
	l_motor.stop(stop_action = "hold")
	r_motor.stop(stop_action = "hold")

#
def calibrate_gyro():
	gy.mode = "GYRO-RATE"
	gy.mode = "GYRO-ANG"

	time.sleep(4)

	angle = gy.value()

#
def correct_drift():
	scaled_error = (heading - angle)/25
	max_error = (max_speed / base_speed) - 1:


	if scaled_error < -max_error:
		scaled_error = -max_error

	elif scaled_error > max_error:
		scaled_error = max_error

	l_motor.speed_sp = base_speed - (base_speed * scaled_error)
	r_motor.speed_sp = base_speed + (base_speed * scaled_error)

#
def turn(speed_reduction):
	if angle < heading:
		m.speed_sp = -base_speed * speed_reduction
		m.speed_sp = base_speed * speed_reduction
	
	if angle > heading:
		m.speed_sp = base_speed * speed_reduction
		m.speed_sp = -base_speed * speed_reduction
		
#
def update_visuals():
	LCD_screen.clear()

	LCD_screen.draw.ellipse((20, 20, 60, 60))
	LCD_screen.draw.ellipse((118, 20, 158, 60))

	if canSee:
		LCD_screen.draw.arc((20, 80, 158, 100), 0, 180)
		
		Leds.set_color(Leds.LEFT, Leds.GREEN)
		Leds.set_color(Leds.RIGHT, Leds.GREEN)
	
	else:
		LCD_screen.draw.arc((20, 80, 158, 100), 180, 360)

		Leds.set_color(Leds.LEFT, Leds.RED)
		Leds.set_color(Leds.RIGHT, Leds.RED)

	lcd.update()


calibrate_gyro()

update_visuals()

Sound.tone([(1500, 500, 100), (1000, 500, 0)]).wait()


while True:
	while distance > min_distance:
		correct_drift()
		run_motors()

		angle = gy.value()
		distance = ir.value()

	stop_motors()

	canSee = False
	update_visuals()

	Sound.tone(1500, 1000).wait()

	time.sleep(3)

	distance = ir.value()

	if distance < min_distance:
		Sound.tone(1500, 1000).wait()

		direction = 1

		heading = 90 * direction
		angle = gy.value()

		while heading != angle:
			turn(turn_speed_reduction, angle)
			run_motors()
			angle = gy.value()

		stop_motors()
		calibrate_gyro()
		
		heading = 0

		distance = ir.value()

	canSee = True
	update_visuals()

	Sound.tone(1000, 1000).wait()
