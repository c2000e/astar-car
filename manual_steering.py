#!/usr/bin/env python3
from ev3dev.ev3 import *
from time import sleep

from random import choice

import pickle
import socket as socket_library

HOST = ""
PORT = 9999

LEGO_SLOPE = 3.6

QUEUE_CONTROL = 0
MANUAL_CONTROL = 1
A_STAR = 2
CELEBRATE = 3

OFF = 0
ON = 1

LEFT_MOTOR = 0
RIGHT_MOTOR = 1

# Messages sent to the server for handling
ACCEPT_MSG = pickle.dumps("Directions accepted.", protocol = 0)
DECLINE_MSG = pickle.dumps("Directions invalid", protocol = 0)
SUCCESS_MSG = pickle.dumps("Directions completed.", protocol = 0)
FAILURE_MSG = pickle.dumps("Direction completion failed.", protocol = 0)


# Constants for colors that should be recognized by the program
UNKNOWN = 0
BLACK = 1
YELLOW = 4
WHITE = 6

COLORS = [UNKNOWN, BLACK, YELLOW, WHITE]

# How many sensor readings should be stored to check for errors
COLOR_MEMORY_LENGTH = 10

MIN_DISTANCE = 50

# Percentages used to control how the robot reacts to changes in color
# calculated by dividing amount of a color by the color memory length

# Road threshold determines how many times the robot can detect a color besides black, white, and yellow before shutting off
# The feature is currently unused (the threshold is set at greater than 100%)
ROAD_THRESHOLD = 1.1

# Node threshold determines how many times the robot needs to see yellow before reacting to the node
NODE_THRESHOLD = 0.3

# Constants used to store turning directions
# Switch to numbers? Used to cause issues, need to check if still issue
LEFT = "left"
RIGHT = "right"
STRAIGHT = "straight"
REVERSE = "reverse"

# Integer value between 0 and 1000 that limits the speed of the motors.
MAX_SPEED = 360

# Float value that is used to keep track of how far off track the robot is when exiting a node.
error = 0

# Float value that determines how severely the robot reacts to being in the wrong location while following the road.
adjustment = 0.1

# Float value that is muliplied by the robot's max speed to slow down the robot during turns to increase accuracy.
turn_speed_reduction = 0.2

# Boolean value (1 or -1) that decides whether the robot should expect black to be on the left or right side of the robot's center.
# 1 is equivalent to black on the left, -1 is equivalent to black on the right
black_side = 1

# Counter used to keep track of how long the robot has been waiting on an obstacle to move
obstacle_detected_counter = 0

# How many times the robot will wait for an obstacle to move
obstacle_wait_timeout = 2

# A list of empty strings which is later used to keep track of past color sensor readings which are used for error tracking
past_colors = []
for i in range(COLOR_MEMORY_LENGTH):
	past_colors.append("")


# Used as a killswitch while the robot is running
btn = Button()


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


# Creates a socket object used to connect to the server
socket = socket_library.socket(socket_library.AF_INET, socket_library.SOCK_STREAM)


# Runs the motors until stopped while also allowing easy adjustment of speed.
def run_motors():
	l_motor.run_forever()
	r_motor.run_forever()


# Forces both motors to stop immediately.
def stop_motors():
	l_motor.speed_sp = 0
	r_motor.speed_sp = 0

	l_motor.stop(stop_action = "hold")
	r_motor.stop(stop_action = "hold")


# Updates list of past colors and calculates how frequent a color is seen which is used to determine the robot's location
def detect_color():
	global COLORS
	global past_colors

	current_color = cl.value()

	for i in range(len(past_colors) - 1):
		past_colors[i] = past_colors[i + 1]
	
	past_colors[len(past_colors) - 1] = current_color

	percent_unknown = past_colors.count(UNKNOWN) / len(past_colors)
	percent_black = past_colors.count(BLACK) / len(past_colors)
	percent_yellow = past_colors.count(YELLOW) / len(past_colors)
	percent_white = past_colors.count(WHITE) / len(past_colors)

	return(percent_unknown, percent_black, percent_yellow, percent_white)


# Changes the speed of the motors to make the robot follow a line.
# Uses LEGO's predefined color ranges
def follow_road():
	global error
	global black_side

	current_color = cl.value()

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


#
def check_for_obstacles():
	global obstacle_detected_counter

	if ir.value() < MIN_DISTANCE:
		stop_motors()
		obstacle_detected_counter += 1
		Sound.speak("Please move the obstacle out of my driving path. Thank you.").wait()
		sleep(10)

	# collision check
	elif ts.value():
		stop_motors()
		obstacle_detected_counter += 1
		Sound.speak("Please move the obstacle out of my driving path. Thank you.").wait()
		sleep(10)

	else:
		obstacle_detected_counter = 0


# Ensures the robot turns and exits a node in the correct order
def handle_node(turn_direction):
	global past_colors
	global black_side

	stop_motors()

	# Turn if the robot isn't going straight
	if turn_direction != STRAIGHT:
		turn(turn_direction)

	# Change which side the robot should expect to see black on if its going straight or turning completely around
	if turn_direction == STRAIGHT or turn_direction == REVERSE:
		black_side *= -1

	# Leave the node
	exit_node()

	# Reset the color memory
	past_colors = []
	for i in range(COLOR_MEMORY_LENGTH):
		past_colors.append("")	


#
def handle_failure():
	stop_motors()

	socket_connection.sendall(FAILURE_MSG)
	socket_connection.shutdown(socket_library.SHUT_RDWR)
	socket_connection.close()

	exit()


#
def handle_success():
	print("Success!")


# No longer used; returns random direction from a list of possible directions
def get_directions():
	global black_side

	turn_direction = choice(DIRECTIONS)
	
	if turn_direction == STRAIGHT:
		black_side *= -1

	return(turn_direction)


# Ensures the robot can turn in any direction and end up where expected
def turn(turn_direction):
	global black_side

	# becomes true when a specific waypoint during the turn has been detected
	half_turn_complete = False

	# becomes true when the turn has been completed
	turn_complete = False

	# updates the reading from the color sensor
	current_color = cl.value()
	
	while not turn_complete:
		global obstacle_detected_counter

		check_for_obstacles()

		if obstacle_detected_counter > obstacle_wait_timeout:
			handle_failure()

		elif obstacle_detected_counter == 0:
			# if black is on the left
			if black_side == 1:
				if turn_direction == LEFT:
					if current_color != BLACK:
						r_motor.speed_sp = MAX_SPEED * turn_speed_reduction
					else:
						turn_complete = True

				elif turn_direction == RIGHT:
					if half_turn_complete != True:
						if current_color != BLACK:
							l_motor.speed_sp = MAX_SPEED * turn_speed_reduction
						
						else:
							half_turn_complete = True

					elif current_color != WHITE:
						l_motor.speed_sp = MAX_SPEED * turn_speed_reduction
					
					else:
						turn_complete = True

				elif turn_direction == REVERSE:
					if half_turn_complete != True:
						if current_color != BLACK:
							l_motor.speed_sp = -MAX_SPEED * turn_speed_reduction
							r_motor.speed_sp = MAX_SPEED * turn_speed_reduction
						else:
							half_turn_complete = True

					elif current_color != WHITE:
						l_motor.speed_sp = -MAX_SPEED * turn_speed_reduction
						r_motor.speed_sp = MAX_SPEED * turn_speed_reduction
					
					else:	
						turn_complete = True

			# if black is on the right
			elif black_side == -1:
				if turn_direction == LEFT:
					if half_turn_complete != True:
						if current_color != BLACK:
							r_motor.speed_sp = MAX_SPEED * turn_speed_reduction
						else:
							half_turn_complete = True
					elif current_color != WHITE:
						r_motor.speed_sp = MAX_SPEED * turn_speed_reduction
					else:
						turn_complete = True

				elif turn_direction == RIGHT:
					if current_color != BLACK:
						l_motor.speed_sp = MAX_SPEED * turn_speed_reduction
					else:
						turn_complete = True

				elif turn_direction == REVERSE:
					if half_turn_complete != True:
						if current_color != BLACK:
							l_motor.speed_sp = MAX_SPEED * turn_speed_reduction
							r_motor.speed_sp = -MAX_SPEED * turn_speed_reduction
						else:
							half_turn_complete = True

					elif current_color != WHITE:
						l_motor.speed_sp = MAX_SPEED * turn_speed_reduction
						r_motor.speed_sp = -MAX_SPEED * turn_speed_reduction
					
					else:	
						turn_complete = True


			# runs the motors at the new speeds
			run_motors()

			# updates the reading from the color sensor
			current_color = cl.value()

	stop_motors()


# Ensures the robot stays on the road when leaving a node
# This implementation will only work on black and white roads as it aims for a reflection value which occurs at the intersection of black and white
def exit_node():
	target_reflection = 35
	cl.mode = "COL-REFLECT"

	for i in range(300):
		error = (target_reflection - cl.value())

		l_speed = (LEGO_SLOPE * error * black_side) + MAX_SPEED
		r_speed = (-LEGO_SLOPE * error * black_side) + MAX_SPEED

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
socket_connection, client_ip = socket.accept()
print("Connected to ", client_ip)

while True:
	ser_direction_queue = socket_connection.recv(1024)

	# Error checking needs to happen between here...

	direction_queue = pickle.loads(ser_direction_queue)
	direction_queue_length = len(direction_queue) - 1

	# ...and here

	socket_connection.sendall(ACCEPT_MSG)

	mode = direction_queue[direction_queue_length]

	if mode == QUEUE_CONTROL:
		# killswitch
		if btn.any():
			exit()

		else:
			for i in range(direction_queue_length):
				turn_direction = direction_queue[i]

				while True:
					color_percents = detect_color()

					if (color_percents[0] < ROAD_THRESHOLD) and (color_percents[2] < NODE_THRESHOLD):
						follow_road()

					elif color_percents[2] >= NODE_THRESHOLD:
						handle_node(turn_direction)
						break

					else:
						handle_failure()
						break


	elif mode == MANUAL_CONTROL:
		# killswitch
		if btn.any():
			exit()

		else:
			l_motor.speed_sp = MAX_SPEED
			r_motor.speed_sp = MAX_SPEED

			if direction_queue[LEFT_MOTOR] == ON:
				l_motor.run_timed(time_sp = 100)

			else:
				l_motor.stop(stop_action = "hold")

			if direction_queue[RIGHT_MOTOR] == ON:
				r_motor.run_timed(time_sp = 100)

			else:
				r_motor.stop(stop_action = "hold")


	elif mode == A_STAR:
		for i in range(direction_queue_length + 1):
			if i < direction_queue_length:
				turn_direction = direction_queue[i]

			while True:
				check_for_obstacles()

				# killswitch
				if btn.any():
					handle_failure()

				# has the robot already waited on an obstacle to move?
				elif obstacle_detected_counter > obstacle_wait_timeout:
					Sound.speak("Obstacle has not moved. Exiting.")
					handle_failure()

				# normal operations
				elif obstacle_detected_counter == 0:
					color_percents = detect_color()

					if (color_percents[0] < ROAD_THRESHOLD) and (color_percents[2] < NODE_THRESHOLD):
						follow_road()

					elif color_percents[2] >= NODE_THRESHOLD:
						if i < direction_queue_length:
							handle_node(turn_direction)
							stop_motors()
							break

						else:
							stop_motors()
							break

					else:
						handle_failure()

		socket_connection.sendall(SUCCESS_MSG)

	elif mode == CELEBRATE:
		Sound.speak("Arrived at destination.").wait()
		sleep(5)
		Sound.speak("Returning home.").wait()

		socket_connection.sendall(SUCCESS_MSG)

	else:
		print("INVALID MODE")
		print("Exiting program")
		break


# Stops the robot and notifies the user with a beep.
stop_motors()
Sound.beep()

# Python default function which ensures the program ends correctly
exit()
