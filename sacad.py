#!/usr/bin/env python3
from ev3dev.ev3 import *
from time import sleep

l_motor = LargeMotor(OUTPUT_B)
assert l_motor.connected, "Connect left motor to port B."

r_motor = LargeMotor(OUTPUT_C)
assert r_motor.connected, "Connect right motor to port C."

btn = Button()

while not btn.any():
	l_motor.run_timed(time_sp = 4000, speed_sp = 480)
	r_motor.run_timed(time_sp = 4000, speed_sp = 100)
	r_motor.wait_while("running")

	r_motor.run_timed(time_sp = 4000, speed_sp = 480)
	l_motor.run_timed(time_sp = 4000, speed_sp = 100)
	l_motor.wait_while("running")