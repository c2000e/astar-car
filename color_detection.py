#!/usr/bin/env python3
from ev3dev.ev3 import *
from time import sleep


cl = ColorSensor()
assert cl.connected, "Connect color sensor"

ir = InfraredSensor()
assert ir.connected, "Connect IR sensor"

ts = TouchSensor()
assert ts.connected, "Connect touch sensor"

l_motor = LargeMotor(OUTPUT_B)
r_motor = LargeMotor(OUTPUT_C)

cl.mode = "COL-REFLECT"
ir.mode = "IR-PROX"

base_speed = 180

target_reflection = 35

error_scale = 1.15

direction = 1

def run_motors():
	l_motor.run_forever()
	r_motor.run_forever()

def stop_motors():
	l_motor.stop(stop_action = "hold")
	r_motor.stop(stop_action = "hold")

def follow_line():
	error = (target_reflection - cl.value()) * error_scale

	l_speed = (-7.2 * error * direction) + base_speed
	r_speed = (7.2 * error * direction) + base_speed

	if l_speed > base_speed:
		l_speed = base_speed
	if r_speed > base_speed:
		r_speed = base_speed
	
	l_motor.speed_sp = l_speed
	r_motor.speed_sp = r_speed

while not (ts.value() or ir.value() < 35):
	follow_line()
	run_motors()

stop_motors()
Sound.beep()
