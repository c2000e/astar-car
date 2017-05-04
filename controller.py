import msvcrt
import pickle
import requests
import socket

from pypaths import astar


# Possible modes
QUEUE_CONTROL = 0
MANUAL_CONTROL = 1
A_STAR = 2

# HOST_IP needs to match ev3's
HOST_IP = "209.114.105.223"
PORT = 9999

# Dimensions of grid
GRID_HEIGHT = 6
GRID_WIDTH = 6

# For readability
OFF = 0
ON = 1

# Makes list indexing easier to read
X = 0
Y = 1

# Makes orientation easier to understand
NORTH = 0
EAST = 1
SOUTH = 2
WEST = 3

# Switch to numbers? Used to cause issues, need to check if still issue
LEFT = "left"
RIGHT = "right"
STRAIGHT = "straight"
REVERSE = "reverse"

# List of all nodes within the grid dimensions
VALID_NODES = []
for y in range(GRID_HEIGHT):
    for x in range(GRID_WIDTH):
        node_coord = (x, y)
        VALID_NODES.append(node_coord)

# Tuple that holds coordinates for where the robot should return
HOME_NODE = (0, 0)

# Partial URL for library database
BASE_URL = "http://bigcat.fhsu.edu/newmedia/projects/stacks/robotStackToNode.php?stackID="

# Socket connections require a string to be sent when the connection ends
DISCONNECT_MESSAGE = "DISCONNECT"


mode = 2
orientation = NORTH

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

    print("Directions sent successfully")


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


def get_target_node():
    target_node = None

    while target_node is None:
        target_stack_id = raw_input("target stack id: ")
        complete_url = BASE_URL + target_stack_id

        r = requests.get(complete_url)

        target_node_id = int(r.content)
        if target_node_id < 1:
            print("Invalid Target Node ID")

        else:
            target_node = VALID_NODES[target_node_id]

    return(target_node)


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

        return [c for c in neighbor_list
                if c != coord
                and c[0] >= 0 and c[0] < width
                and c[1] >= 0 and c[1] < height]

    return func


def find_path(current_node, target_node):
    finder = astar.pathfinder(neighbors = grid_neighbors(GRID_HEIGHT, GRID_WIDTH))
    path_info = finder(current_node, target_node)

    return(path_info)


def update_orientation(turn_direction, orientation):
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

    elif turn_direction == REVERSE:
        if orientation == SOUTH:
            orientation = NORTH

        elif orientation == WEST:
            orientation = EAST

        else:
            orientation += 2

    return(orientation)


def path_to_directions(path_length, path_coord):
    global orientation

    direction_queue = []
    for i in range(path_length):
        if path_coord[i][X] < path_coord[i + 1][X]:
            if orientation == NORTH:
                turn_direction = RIGHT

            elif orientation == EAST:
                turn_direction = STRAIGHT

            elif orientation == SOUTH:
                turn_direction = LEFT

            elif orientation == WEST:
                turn_direction = REVERSE

            else:
                print("INVALID ORIENTATION")

        elif path_coord[i][X] > path_coord[i + 1][X]:
            if orientation == NORTH:
                turn_direction = LEFT

            elif orientation == EAST:
                turn_direction = REVERSE

            elif orientation == SOUTH:
                turn_direction = RIGHT

            elif orientation == WEST:
                turn_direction = STRAIGHT

            else:
                print("INVALID ORIENTATION")

        elif path_coord[i][Y] < path_coord[i + 1][Y]:
            if orientation == NORTH:
                turn_direction = STRAIGHT

            elif orientation == EAST:
                turn_direction = LEFT

            elif orientation == SOUTH:
                turn_direction = REVERSE

            elif orientation == WEST:
                turn_direction = RIGHT

            else:
                print("INVALID ORIENTATION")

        elif path_coord[i][Y] > path_coord[i + 1][Y]:
            if orientation == NORTH:
                turn_direction = REVERSE

            elif orientation == EAST:
                turn_direction = RIGHT

            elif orientation == SOUTH:
                turn_direction = STRAIGHT

            elif orientation == WEST:
                turn_direction = LEFT

            else:
                print("INVALID ORIENTATION")

        else:
            print("INVALID COORDINATES; UNABLE TO CALCULATE PATH")

        orientation = update_orientation(turn_direction, orientation)

        direction_queue.append(turn_direction)

    return(direction_queue)


def a_star(current_node):
    if current_node == HOME_NODE:
        target_node = get_target_node()

    else:
        target_node = HOME_NODE

    path_info = find_path(current_node, target_node)

    path_length = path_info[0]
    path_coord = path_info[1]
    
    current_node = path_coord[path_length]

    direction_queue = path_to_directions(path_length, path_coord)
    print(direction_queue)

    return(direction_queue, current_node)


socket_connection.connect((HOST_IP, PORT))

while True:
    if mode == QUEUE_CONTROL:
        directions = queue_control()
        directions.append(QUEUE_CONTROL)
        send_data(directions, socket_connection)

    elif mode == MANUAL_CONTROL:
        manual_control()

    elif mode == A_STAR:
        directions, current_node = a_star(HOME_NODE)
        directions.append(A_STAR)
        send_data(directions, socket_connection)

        print("Waiting for robot to reach destination.")
        socket_connection.recv(1024)
        print("Robot reached destination. Returning home.")

        directions, current_node = a_star(current_node)
        directions.append(A_STAR)
        send_data(directions, socket_connection)

        print("Waiting for robot to reach destination.")
        socket_connection.recv(1024)
        print("Robot returned home.")


    else:
        print("NOT A VALID MODE")
        socket_connection.send_all(DISCONNECT_MESSAGE)
        socket_connection.close()
        break
