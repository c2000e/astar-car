from ev3dev.ev3 import *
from time import sleep


MAX_SPEED = 360
TARGET_REFLECTION = 35
LEGO_SLOPE = 3.6


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


cl.mode = "COL-REFLECT"

ir.mode = "IR-PROX"


# Runs the motors until stopped while also allowing easy adjustment of speed.
def run_motors():
	l_motor.run_forever()
	r_motor.run_forever()

def stop_motors():
	l_motor.stop(stop_action = "hold")
	r_motor.stop(stop_action = "hold")

	l_motor.speed_sp = 0
	r_motor.speed_sp = 0


while True:
	while (ir.value() > 50) and (ts.value != 1):
		error = (target_reflection - cl.value())
		print(error)

		#if error > 70:
		#	l_speed = 0


		l_speed = MAX_SPEED * error
		r_speed = MAX_SPEED * error

		#l_speed = (LEGO_SLOPE * error) + MAX_SPEED
		#r_speed = (-LEGO_SLOPE * error) + MAX_SPEED

		if l_speed > MAX_SPEED:
			l_speed = MAX_SPEED
		elif l_speed < -MAX_SPEED:
			l_speed = -MAX_SPEED
		else:
			print("")

		if r_speed > MAX_SPEED:
			r_speed = MAX_SPEED
		elif r_speed < -MAX_SPEED:
			r_speed = -MAX_SPEED
		else:
			print("")
		
		l_motor.speed_sp = l_speed
		r_motor.speed_sp = r_speed

		run_motors()

	stop_motors()
	sleep(3)