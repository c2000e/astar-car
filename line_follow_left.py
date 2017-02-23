#!/usr/bin/env python3
from ev3dev.ev3 import *
from time import sleep


UNKNOWN = 0
BLACK = 1
YELLOW = 4
RED = 5
WHITE = 6
BROWN = 7


# Integer value between 0 and 1000 that limits the speed of the motors.
max_speed = 180

# Integer value between 0 and 100 that the robot tries to get the color sensor (in reflection mode) to return.
# 35 is the approximate reflection value above the intersection of a white and black line.
target_reflection = 35

target_color = BLACK
left_color = YELLOW
right_color = WHITE

# Float value greater than 0 that determines how severely the robot reacts to error.
# Larger values cause larger corrections.
error_scale = 1.15
adjustment = 0.05
error = 0

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


# Sets color sensor to measure reflection intensity.
cl.mode = "COL-COLOR"

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

def drive():
	global error

	current_color = cl.value()

	if current_color == BLACK:
		if error > 0:
			error -= adjustment
		if error < 0:
			error += adjustment	

	elif current_color == YELLOW:
		error += adjustment

	elif current_color == WHITE:
		error -= adjustment
	
	if error > 1:
		error = 1
	elif error < -1:
		error = -1

	left_motor_speed = (-1 * max_speed * error) + max_speed
	right_motor_speed = (max_speed * error) + max_speed

	if left_motor_speed > max_speed:
		left_motor_speed = max_speed
	elif left_motor_speed < -max_speed:
		left_motor_speed = -max_speed

	if right_motor_speed > max_speed:
		right_motor_speed = max_speed
	elif right_motor_speed < -max_speed:
		right_motor_speed = -max_speed

	l_motor.speed_sp = left_motor_speed
	r_motor.speed_sp = right_motor_speed


def follow_line():
	# Calculates error based on a target reflection value and actual reflection value.
	# This value is multiplied by a float (error_scale) that allows adjustment of how severely the robot reacts to errors.
	error = (target_reflection - cl.value()) * error_scale

	

	# Modeled after ev3 steering function; y = (7.2 * Steering) + Power.
	# "Steering" becomes "error" and "Power" becomes max_speed.
	# The direction variable changes whether the sensor tracks the right or left side of a black line bordered by a white line.
	l_speed = (-7.2 * error * direction) + max_speed
	r_speed = (7.2 * error * direction) + max_speed

	# Limits both motors to a maximum speed, similar to the original ev3 software.
	if l_speed > max_speed:
		l_speed = max_speed
	if r_speed > max_speed:
		r_speed = max_speed
	
	# Sets motors to run at their calculated speed.
	l_motor.speed_sp = l_speed
	r_motor.speed_sp = r_speed


# Runs only while the touch sensor is not activated and the infrared sensor doesn't detect anything within approximately 35 cm.
while not ts.value(): #or ir.value() < 50):
	#follow_line()
	drive()
	run_motors()

# Stops the robot and notifies the user with a beep.
stop_motors()
Sound.beep()
