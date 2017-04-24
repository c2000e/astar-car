mport pickle
import msvcrt
import socket


QUEUE_CONTROL = 0
MANUAL_CONTROL = 1
A_STAR = 2

HOST_IP = "209.114.107.188"
PORT = 9999

GRID_HEIGHT = 6
GRID_WIDTH = 6

OFF = 0
ON = 1

NORTH = 0
EAST = 1
SOUTH = 2
WEST = 3

LEFT = "left"
RIGHT = "right"
STRAIGHT = "straight"

DISCONNECT_MESSAGE = "DISCONNECT"

mode = 0
orientation = NORTH
starting_node = (0,0)

possible_nodes = []
for y in range(GRID_HEIGHT):
    for x in range(GRID_WIDTH):
        node_coord = (x, y)
        possible_nodes.append(node_coord)

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
			direction_queue = [LEFT, LEFT, RIGHT, RIGHT, RIGHT, RIGHT, LEFT]
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
	global socket_connection

	while True:
		key = msvcrt.getwch()

		if key == "w":
			left_motor = ON
			right_motor = ON

		elif key == "a":
			left_motor = OFF
			right_motor = ON

		elif key == "d":
			left_motor = ON
			right_motor = OFF

		else:
			left_motor = OFF
			right_motor = OFF

		directions = [left_motor, right_motor, MANUAL_CONTROL]

		send_data(directions, socket_connection)

def a_star():
	#starting_x = int(raw_input("start x: "))
	#starting_y = int(raw_input("start y: "))
	starting_location = (0,0)

	target_node_id = -1
	while target_node_id == -1:
    	target_node_id = int(raw_input("target node [0 - 35]: "))
    	if target_node_id in range(GRID_WIDTH * GRID_HEIGHT):
        	print("Input accepted")
        
    	else:
        	target_node_id = -1
        	print("Invalid input")

    target_node = possible_nodes[target_node_id]

    finder = astar.pathfinder(neighbors = grid_neighbors(GRID_HEIGHT, GRID_WIDTH))
	path = finder(starting_location, ending_location)

	path_length = path[0]
	path_coord = path[1]

	direction_queue = []
	for i in range(path_length):
		if path_coord[i][X] < path_coord[i + 1][X]:
	        if orientation == NORTH:
	            turn_direction = RIGHT

	        elif orientation == EAST:
	            turn_direction = STRAIGHT

	        elif orientation == SOUTH:
	            turn_direction = LEFT

	        else:
	            print("ERROR")

	    elif path_coord[i][X] > path_coord[i + 1][X]:
	        if orientation == NORTH:
	            turn_direction = LEFT

	        elif orientation == SOUTH:
	            turn_direction = RIGHT

	        elif orientation == WEST:
	            turn_direction == STRAIGHT

	        else:
	            print("ERROR")

	    elif path_coord[i][Y] < path_coord[i + 1][Y]:
	        if orientation == NORTH:
	            turn_direction = STRAIGHT

	        elif orientation == EAST:
	            turn_direction = LEFT

	        elif orientation == WEST:
	            turn_direction = RIGHT

	        else:
	            print("ERROR")

	    elif path_coord[i][Y] > path_coord[i + 1][Y]:
	        if orientation == EAST:
	            turn_direction = RIGHT

	        elif orientation == SOUTH:
	            turn_direction = STRAIGHT

	        elif orientation == WEST:
	            turn_direction = LEFT

	        else:
	            print("ERROR")

	    else:
	        print("error")


	    if turn_direction == LEFT:
	        if orientation == NORTH:
	            orientation = WEST

	        else:
	            orientation -= 1

	    elif turn_direction == RIGHT:
	        if orientation == WEST:
	            orientation = NORTH
	            
	        else:
	            orientation += 1
	            
	    direction_queue.append(turn_direction)

	return(direction_queue)

def grid_neighbors(height, width):
    def func(coord):
        neighbor_list = [(coord[X], coord[Y] + 1),
                         (coord[X], coord[Y] - 1),
                         (coord[X] + 1, coord[Y]),
                         (coord[X] - 1, coord[Y])]

        if coord[Y] % 2 == 0:
            del neighbor_list[3]
            del neighbor_list[2]
            
            if coord[Y] <= 0:
                del neighbor_list[1]

            if coord[Y] + 1 >= height:
                del neighbor_list[0]

        else:
            if coord[X] - 1 <= 0:
                del neighbor_list[3]

            if coord[X] + 1 >= width:
                del neighbor_list[2]

        return [c for c in neighbor_list
                if c != coord
                and c[0] >= 0 and c[0] < width
                and c[1] >= 0 and c[1] < height]

    return func


socket_connection.connect((HOST_IP, PORT))
connected = True

while connected:
	if mode == QUEUE_CONTROL:
		directions = queue_control()
		directions.append(QUEUE_CONTROL)
		send_data(directions, socket_connection)

	elif mode == MANUAL_CONTROL:
		manual_control()

	elif mode == A_STAR:
		directions = a_star()
		directions.append(A_STAR)
		send_data(directions, socket_connection)

	else:
		print("NOT A VALID MODE")
		

socket_connection.send_all(DISCONNECT_MESSAGE)
socket_connection.close()
