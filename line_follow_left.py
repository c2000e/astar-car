#!/usr/bin/env python3
from ev3dev.ev3 import *
from time import sleep


UNKNOWN = 0
BLACK = 1
YELLOW = 4
RED = 5
WHITE = 6
BROWN = 7

LEFT = -90


# Integer value between 0 and 1000 that limits the speed of the motors.
max_speed = 360

adjustment = 0.05
error = 0

heading = 0

turn_speed_reduction = 0.2


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


#
def calibrate_gyro():
	gr.mode = "GYRO-RATE"
	gr.mode = "GYRO-ANG"
	time.sleep(4)


# Runs the motors until stopped while also allowing easy adjustment of speed.
def run_motors():
	l_motor.run_forever()
	r_motor.run_forever()


# Forces both motors to stop immediately.
def stop_motors():
	l_motor.stop(stop_action = "hold")
	r_motor.stop(stop_action = "hold")


# Changes the speed of the motors to make the robot follow a line.

def follow_road():
	global error

	current_color = cl.value()

	if current_color == RED:
		stop_motors()
		time.sleep(1)
		handle_node()

	else:
		if current_color == BLACK:
			error -= adjustment

		elif current_color == WHITE:
			error += adjustment
		
		if error > 0.15:
			error = 0.15
		elif error < -0.15:
			error = -0.15

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

		run_motors()


def handle_node():
	turn_direction = get_directions()
	turn(turn_direction)
	exit_node()


def get_directions():
	return(LEFT)


def turn(turn_direction):
	global heading

	heading += turn_direction

	angle = gr.value()

	while angle != heading:
		if angle < heading:
			l_motor.speed_sp = -max_speed * turn_speed_reduction
			r_motor.speed_sp = max_speed * turn_speed_reduction
	
		if angle > heading:
			l_motor.speed_sp = max_speed * turn_speed_reduction
			r_motor.speed_sp = -max_speed * turn_speed_reduction

		angle = gr.value()

	stop_motors()


def exit_node():
	current_color = cl.value()

	while current_color != (BLACK or WHITE):
		l_motor.speed_sp = 180
		r_motor.speed_sp = 180

		run_motors()
		current_color = cl.value()

	stop_motors()


calibrate_gyro()

# Runs only while the touch sensor is not activated and the infrared sensor doesn't detect anything within approximately 35 cm.
while not ts.value():
	follow_road()

# Stops the robot and notifies the user with a beep.
stop_motors()
Sound.beep()
