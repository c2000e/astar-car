from random import *
from ev3dev.ev3 import *


LEFT = "left"
RIGHT = "right"
STRAIGHT = "straight"
REVERSE = "reverse"

LEGO_SLOPE = 3.6


# Constants for colors that should be recognized by the program
UNKNOWN = 0
BLACK = 1
YELLOW = 4
WHITE = 6


# Integer value between 0 and 1000 that limits the speed of the motors.
MAX_SPEED = 360

# Float value that is used to keep track of how far off track the robot is.
error = 0

# Float value that determines how severely the robot reacts to being in the wrong location.
adjustment = 0.1

# Float value that is muliplied by the robot's max speed to slow down the robot during turns to increase accuracy.
turn_speed_reduction = 0.2

# Boolean value (1 or -1) that decides whether the robot should expect black to be on the left or right side of the robot's center.
black_side = 1

direction_queue = [RIGHT, RIGHT, RIGHT, RIGHT, RIGHT, RIGHT]

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


def handle_failure():
	stop_motors()


def handle_success():
	print("Success!")


# Changes the speed of the motors to make the robot follow a line.
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


def handle_node(turn_index):
	global black_side

	stop_motors()

	turn_direction = get_directions(turn_index)

	if turn_direction != STRAIGHT:
		turn(turn_direction)

	if turn_direction == STRAIGHT or turn_direction == REVERSE:
		black_side *= -1

	exit_node()


def turn(turn_direction):
	global black_side

	turn_complete = False

	heading = turn_direction

	current_color = cl.value()
	
	while not turn_complete:
		if black_side == 1:
			if turn_direction == LEFT:
				if current_color != BLACK:
					l_motor.speed_sp = -MAX_SPEED * turn_speed_reduction
					r_motor.speed_sp = MAX_SPEED
				else:
					turn_complete = True

			elif turn_direction == RIGHT:
				if current_color != WHITE:
					l_motor.speed_sp = MAX_SPEED
					r_motor.speed_sp = -MAX_SPEED * turn_speed_reduction
				else:
					turn_complete = True

			elif turn_direction == REVERSE:
				if current_color != BLACK:
					l_motor.speed_sp = -MAX_SPEED * turn_speed_reduction
					r_motor.speed_sp = MAX_SPEED
				else:
					turn_complete = True

		elif black_side == -1:
			if turn_direction == LEFT:
				if current_color != WHITE:
					l_motor.speed_sp = -MAX_SPEED * turn_speed_reduction
					r_motor.speed_sp = MAX_SPEED
				else:
					turn_complete = True	

			elif turn_direction == RIGHT:
				if current_color != BLACK:
					l_motor.speed_sp = MAX_SPEED
					r_motor.speed_sp = -MAX_SPEED * turn_speed_reduction
				else:
					turn_complete = True

			elif turn_direction == REVERSE:
				if current_color != WHITE:
					l_motor.speed_sp = -MAX_SPEED * turn_speed_reduction
					r_motor.speed_sp = MAX_SPEED
				else:
					turn_complete = True	


		run_motors()
		current_color = cl.value()

	stop_motors()


def exit_node():
	target_reflection = 35
	cl.mode = "COL-REFLECT"

	for i in range(100):
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


def get_directions(turn_index):
	global black_side

	turn_direction = direction_queue[turn_index]

	return(turn_direction)


for i in range(len(direction_queue)):
	while True:
		if cl.value != YELLOW:
			print("follow")
			follow_road()

		elif cl.value() == YELLOW:
			print("turn")
			handle_node(i)
			break

		else:
			print("fail")
			handle_failure()