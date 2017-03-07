#!/usr/bin/env python3
from ev3dev.ev3 import *
from time import sleep

from random import choice

# Constants for colors that should be recognized by the program
UNKNOWN = 0
BLACK = 1
RED = 5
WHITE = 6

COLORS = [UNKNOWN, BLACK, RED, WHITE]

# Constants for possible directions that the robot may turn.
RIGHT = 94
LEFT = -90
STRAIGHT = 0

DIRECTIONS = [RIGHT]

REASONABLE_DOUBT = 0.6
COLOR_MEMORY_LENGTH = 10


# Integer value between 0 and 1000 that limits the speed of the motors.
max_speed = 540

# Float value that is used to keep track of how far off track the robot is.
error = 0

# Float value that determines how severely the robot reacts to being in the wrong location.
adjustment = 0.05

# Integer value that the robot tries to match with its gyroscope reading during turns.
heading = 0

# Float value that is muliplied by the robot's max speed to slow down the robot during turns to increase accuracy.
turn_speed_reduction = 0.2

# Boolean value (1 or -1) that decides whether the robot should expect black to be on the left or right side of the robot's center.
black_side = 1

past_colors = []
for i in range(COLOR_MEMORY_LENGTH):
	past_colors.append("")


# Initializes color sensor and ensures it is connected.
cl = ColorSensor()
assert cl.connected, "Connect color sensor."

# Initializes gyro sensor and ensures it is connected.
gr = GyroSensor()
assert gr.connected, "Connect gyro sensor."

# Initializes infrared sensor and ensures it is connected.
ir = InfraredSensor()
assert ir.connected, "Connect IR sensor."

# Initializes touch sensor and ensures it is connected.
ts = TouchSensor()
assert ts.connected, "Connect touch sensor."


# Initializes left and right motors and ensures they are connected.
l_motor = LargeMotor(OUTPUT_B)
assert l_motor.connected, "Connect left motor to port B."

r_motor = LargeMotor(OUTPUT_C)
assert r_motor.connected, "Connect right motor to port C."


# Sets color sensor to return an integer value representative of the color its seeing.
cl.mode = "COL-COLOR"

# Sets infrared sensor to measure proximity on a scale of 0% - 100%.
# 0% is equivalent to 0 cm and 100% is approximately 70 cm.
ir.mode = "IR-PROX"


# Ensures that the gyro is oriented in the correct direction.
def calibrate_gyro():
	gr.mode = "GYRO-RATE"
	gr.mode = "GYRO-ANG"
	sleep(4)


# Runs the motors until stopped while also allowing easy adjustment of speed.
def run_motors():
	l_motor.run_forever()
	r_motor.run_forever()


# Forces both motors to stop immediately.
def stop_motors():
	l_motor.stop(stop_action = "hold")
	r_motor.stop(stop_action = "hold")

	l_motor.speed_sp = 0
	r_motor.speed_sp = 0


def detect_color():
	global COLORS
	global past_colors

	current_color = cl.value()

	for i in range(len(past_colors) - 1):
		past_colors[i] = past_colors[i + 1]
	
	past_colors[len(past_colors) - 1] = current_color

	percent_unknown = past_colors.count(UNKNOWN) / len(past_colors)
	percent_black = past_colors.count(BLACK) / len(past_colors)
	percent_red = past_colors.count(RED) / len(past_colors)
	percent_white = past_colors.count(WHITE) / len(past_colors)

	return(percent_unknown, percent_black, percent_red, percent_white)


# Changes the speed of the motors to make the robot follow a line.
def follow_road():
	global error
	global black_side

	current_color = cl.value()
	color_percents = detect_color()

	if (color_percents[0] < REASONABLE_DOUBT) and (color_percents[2] < REASONABLE_DOUBT):
		if current_color == BLACK:
			error -= adjustment

		elif current_color == WHITE:
			error += adjustment
	
		if error > 0.15:
			error = 0.15
		elif error < -0.15:
			error = -0.15

		left_motor_speed = (-1 * max_speed * error * black_side) + max_speed
		right_motor_speed = (max_speed * error * black_side) + max_speed

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

		run_motors()

	elif color_percents[2] > REASONABLE_DOUBT:
		handle_node()

	else:
		handle_failure()


def handle_node():
	global past_colors

	stop_motors()

	turn_direction = get_directions()

	if turn_direction != STRAIGHT:
		turn(turn_direction)

	exit_node()

	past_colors = []
	for i in range(COLOR_MEMORY_LENGTH):
		past_colors.append("")	


def handle_failure():
	stop_motors()


def handle_success():
	print("Success!")


def get_directions():
	global black_side

	turn_direction = choice(DIRECTIONS)
	
	if turn_direction == STRAIGHT:
		black_side *= -1

	return(turn_direction)


def turn(turn_direction):
	heading = turn_direction

	angle = gr.value()

	while angle != heading:
		if angle < heading:
			l_motor.speed_sp = max_speed * turn_speed_reduction
	
		if angle > heading:
			r_motor.speed_sp = max_speed * turn_speed_reduction
		
		run_motors()
		angle = gr.value()

	stop_motors()
	calibrate_gyro()


def exit_node():
	current_color = cl.value()
	while current_color == RED:
		l_motor.speed_sp = max_speed * turn_speed_reduction
		r_motor.speed_sp = max_speed * turn_speed_reduction

		run_motors()

		current_color = cl.value()


calibrate_gyro()

# Runs only while the touch sensor is not activated and the infrared sensor doesn't detect anything within approximately 35 cm.
while not (ts.value() or ir.value() < 50):
	follow_road()

# Stops the robot and notifies the user with a beep.
stop_motors()
Sound.beep()
