from ev3dev.ev3 import *
from time import sleep

l_motor = LargeMotor(OUTPUT_B)
assert l_motor.connected, "Connect left motor to port B."

r_motor = LargeMotor(OUTPUT_C)
assert r_motor.connected, "Connect right motor to port C."

while not btn.any():
	l_motor.run_timed(time_sp = 1000, speed_sp = 360)

	sleep(1)

	l_motor.run_timed(time_sp = 1000, speed_sp = 360)

	sleep(1)

	l_motor.run_timed(time_sp = 1000, speed_sp = 360)

	sleep(1)

	l_motor.run_timed(time_sp = 1000, speed_sp = 360)

	sleep(1)

	r_motor.run_timed(time_sp = 1000, speed_sp = 360)

	sleep(1)

	r_motor.run_timed(time_sp = 1000, speed_sp = 360)

	sleep(1)

	r_motor.run_timed(time_sp = 1000, speed_sp = 360)

	sleep(1)

	r_motor.run_timed(time_sp = 1000, speed_sp = 360)

	sleep(1)