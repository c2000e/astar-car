import pickle
import pygame
import socket


QUEUE_CONTROL = 0
MANUAL_CONTROL = 1
A_STAR = 2

HOST_IP = "209.114.104.54"
PORT = 9999

LEFT = "left"
RIGHT = "right"
STRAIGHT = "straight"

DISCONNECT_MESSAGE = "DISCONNECT"

SCREEN_DIMENSIONS = [500, 700]


mode = 0
is_robot_moving = False

socket_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


def get_typed_direction_queue():
        user_input = False
        possible_inputs = ["left", "right", "straight", "send"]
        direction_queue = []

        while True:
                user_input = raw_input("'left', 'right', or 'straight'. 'send' to deliver instructions to robot: ")

                if user_input in possible_inputs[0:3]:
                	direction_queue.append(user_input)

                elif user_input == possible_inputs[3]:
                	break

                elif user_input == "8":
                	direction_queue = ["left", "left", "right", "right", "right", "right", "left"]
                	break

                else:
                	print("Please input 'left', 'right', 'straight', or 'send'.")

        return(direction_queue)


def send_data(data, socket_connection):
	ser_data = pickle.dumps(data)

	socket_connection.sendall(ser_data)

	while not socket_connection.recv(1024):
		print("Waiting for reply...")

	print("Response recieved!")


def queue_control():
	direction_queue = get_typed_direction_queue()
	return(direction_queue)


def manual_control():
	#control_values = get_controller_input()
	#return(control_values)
	print("NOT FINISHED")


def a_star():
	#return(direction_queue)
	print("NOT FINISHED")


#pygame.init()

socket_connection.connect((HOST_IP, PORT))
connected = True

while connected:
	if mode == QUEUE_CONTROL:
		directions = queue_control()
		directions.append(QUEUE_CONTROL)

	elif mode == MANUAL_CONTROL:
		directions = manual_control()
		directions.append(MANUAL_CONTROL)

	elif mode == A_STAR:
		directions = a_star()
		directions.append(A_STAR)

	else:
		print("NOT A VALID MODE")

	send_data(directions, socket_connection)

socket_connection.send_all(DISCONNECT_MESSAGE)
socket_connection.close()