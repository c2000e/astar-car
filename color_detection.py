#!/usr/bin/env python3
from ev3dev.ev3 import *
from time import sleep


cl = ColorSensor()
assert cl.connected, "Connect color sensor"

ts = TouchSensor()
assert ts.connected, "Connect touch sensor"

l_motor = LargeMotor(OUTPUT_C)
r_motor = LargeMotor(OUTPUT_B)

cl.mode = "COL-REFLECT"


base_speed = 540
max_speed = 900

white = 56
black = 5

error_scale = 0.25


def run_motors():
	l_motor.run_forever()
	r_motor.run_forever()


def stop_motors():
	l_motor.stop(stop_action = "hold")
	r_motor.stop(stop_action = "hold")


def correct_drift():
	left_error = (white - cl.value()) * error_scale
	right_error = (cl.value() - black) * error_scale

	l_motor.speed_sp = base_speed - (base_speed * left_error)
	r_motor.speed_sp = base_speed + (base_speed * right_error)

while not ts.value():
	correct_drift()
	run_motors()

stop_motors()
Sound.beep()