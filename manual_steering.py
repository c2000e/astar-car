#!/usr/bin/env python3
from ev3dev.ev3 import *
from time import sleep

from random import choice

import pickle
import socket

HOST = ""
PORT = 9999

# Constants for colors that should be recognized by the program
UNKNOWN = 0
BLACK = 1
RED = 5
WHITE = 6

COLORS = [UNKNOWN, BLACK, RED, WHITE]

COLOR_MEMORY_LENGTH = 10

REASONABLE_DOUBT = 1

LEFT = 0
STRAIGHT = 1
RIGHT = 2

DIRECTIONS = [RIGHT]

# Integer value between 0 and 1000 that limits the speed of the motors.
MAX_SPEED = 360

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

socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


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

	if current_color == BLACK:
		error -= adjustment

	elif current_color == WHITE:
		error += adjustment

	if error > 0.15:
		error = 0.15
	elif error < -0.15:
		error = -0.15

	left_motor_speed = (-1 * MAX_SPEED * error * black_side) + MAX_SPEED
	right_motor_speed = (MAX_SPEED * error * black_side) + MAX_SPEED

	if left_motor_speed > MAX_SPEED:
		left_motor_speed = MAX_SPEED
	elif left_motor_speed < -MAX_SPEED:
		left_motor_speed = -MAX_SPEED

	if right_motor_speed > MAX_SPEED:
		right_motor_speed = MAX_SPEED
	elif right_motor_speed < -MAX_SPEED:
		right_motor_speed = -MAX_SPEED

	l_motor.speed_sp = left_motor_speed
	r_motor.speed_sp = right_motor_speed

	run_motors()


def handle_node(turn_direction):
	global past_colors

	stop_motors()

	#turn_direction = get_directions()

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
	global black_side

	turn_complete = False

	heading = turn_direction

	current_color = cl.value()
	
	while not turn_complete:
		if black_side == 1:
			if turn_direction == LEFT:
				if not turn_complete:
					if current_color != BLACK:
						l_motor.speed_sp = -MAX_SPEED * turn_speed_reduction
						r_motor.speed_sp = MAX_SPEED
					else:
						turn_complete = True

			elif turn_direction == RIGHT:
				if not turn_complete:
					if current_color != WHITE:
						l_motor.speed_sp = MAX_SPEED
						r_motor.speed_sp = -MAX_SPEED * turn_speed_reduction
					else:
						turn_complete = True

		elif black_side == -1:
			if turn_direction == LEFT:
				if not turn_complete:
					if current_color != WHITE:
						l_motor.speed_sp = -MAX_SPEED * turn_speed_reduction
						r_motor.speed_sp = MAX_SPEED
					else:
						turn_complete = True	

			elif turn_direction == RIGHT:
				if not turn_complete:
					if current_color != BLACK:
						l_motor.speed_sp = MAX_SPEED
						r_motor.speed_sp = -MAX_SPEED * turn_speed_reduction
					else:
						turn_complete = True	


		run_motors()
		current_color = cl.value()

	stop_motors()


def exit_node():
	target_reflection = 35
	cl.mode = "COL-REFLECT"

	for i in range(100):
		error = (target_reflection - cl.value()) * 0.5

		l_speed = (7.2 * error * black_side) + MAX_SPEED
		r_speed = (-7.2 * error * black_side) + MAX_SPEED

		if l_speed > MAX_SPEED:
			l_speed = MAX_SPEED
		if r_speed > MAX_SPEED:
			r_speed = MAX_SPEED
		
		l_motor.speed_sp = l_speed
		r_motor.speed_sp = r_speed

		run_motors()

	stop_motors()
	cl.mode = "COL-COLOR"


socket.bind((HOST, PORT))
socket.listen(1)
connection, client_ip = socket.accept()
print("Connected to ", client_ip)

# Runs only while the touch sensor is not activated and the infrared sensor doesn't detect anything within approximately 35 cm.
while not (ts.value() or ir.value() < 50):
	data = connection.recv(1024)
	turn_direction = pickle.loads(data)

	current_color = cl.value()
	color_percents = detect_color()

	if (color_percents[0] < REASONABLE_DOUBT) and (color_percents[2] < REASONABLE_DOUBT):
		follow_road()

	elif color_percents[2] > 0.1:
		handle_node(turn_direction)
		connection.sendall("Directions completed.")

	else:
		handle_failure()



# Stops the robot and notifies the user with a beep.
stop_motors()
Sound.beep()