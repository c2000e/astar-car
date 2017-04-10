#!/usr/bin/env python3
from ev3dev.ev3 import *
from time import sleep


LEGO_SLOPE = 7.2

# Integer value between 0 and 1000 that limits the speed of the motors.
MAX_SPEED = 180
MIN_SPEED = 60

# Integer value between 0 and 100 that the robot tries to get the color sensor (in reflection mode) to return.
# 35 is the approximate reflection value above the intersection of a white and black line.
TARGET_REFLECTION = 35

# Float value greater than 0 that determines how severely the robot reacts to error.
# Larger values cause larger corrections.
ERROR_SCALE = 1.09

# Boolean value (1 or -1) that determines whether the robot attempts to stay on the left or right side of a black line bordered
# by a white line.
# 1 = Left side of black line
# -1 = Right side of black line
direction = 1


# Initializes color sensor and ensures it is connected.
cl = ColorSensor()
assert cl.connected, "Connect color sensor"

# Initializes infrared sensor and ensures it is connected.
ir = InfraredSensor()
assert ir.connected, "Connect IR sensor"

# Initializes touch sensor and ensures it is connected.
ts = TouchSensor()
assert ts.connected, "Connect touch sensor"

# Initializes left and right motors and ensures they are connected.
l_motor = LargeMotor(OUTPUT_B)
assert l_motor.connected, "Connect left motor to port B"

r_motor = LargeMotor(OUTPUT_C)
assert r_motor.connected, "Connect right motor to port C"

btn = Button()


# Sets color sensor to measure reflection intensity.
cl.mode = "COL-REFLECT"

# Sets infrared sensor to measure proximity on a scale of 0% - 100%.
# 0% is equivalent to 0 cm and 100% is approximately 70 cm.
ir.mode = "IR-PROX"


# Runs the motors until stopped while also allowing easy adjustment of speed.
def run_motors():
	l_motor.run_forever()
	r_motor.run_forever()


# Forces both motors to stop immediately.
def stop_motors():
	l_motor.stop(stop_action = "hold")
	r_motor.stop(stop_action = "hold")


# Changes the speed of the motors to make the robot follow a line.
def follow_line():
	# Calculates error based on a target reflection value and actual reflection value.
	# This value is multiplied by a float (ERROR_SCALE) that allows adjustment of how severely the robot reacts to errors.
	error = (TARGET_REFLECTION - cl.value()) * ERROR_SCALE
	
	# Modeled after ev3 steering function; y = (7.2 * Steering) + Power.
	# "Steering" becomes "error" and "Power" becomes MAX_SPEED.
	# The direction variable changes whether the sensor tracks the right or left side of a black line bordered by a white line.
	l_speed = (LEGO_SLOPE * error) + MAX_SPEED
	r_speed = (-LEGO_SLOPE * error) + MAX_SPEED

	# Limits both motors to a maximum speed, similar to the original ev3 software.
	if l_speed > MAX_SPEED:
		l_speed = MAX_SPEED

	elif l_speed < MIN_SPEED:
		l_speed = MIN_SPEED

	if r_speed > MAX_SPEED:
		r_speed = MAX_SPEED

	elif r_speed < MIN_SPEED:
		r_speed = MIN_SPEED
	
	# Sets motors to run at their calculated speed.
	l_motor.speed_sp = l_speed
	r_motor.speed_sp = r_speed

while True:

	# Runs only while the touch sensor is not activated and the infrared sensor doesn't detect anything within approximately 35 cm.
	while True:
		if btn.enter:
			stop_motors()

			sleep(1)
			while True:
				if btn.enter:
					break

				elif btn.backspace:
					exit()

			sleep(1)

		if (ts.value() or ir.value() < 50):
			stop_motors()
			Sound.beep()

			while True:
				if btn.enter:
					break

				elif btn.backspace:
					exit()

			sleep(1)

		else:
			follow_line()
			run_motors()


# Stops the robot and notifies the user with a beep.
stop_motors()
Sound.beep()