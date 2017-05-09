import msvcrt
import pickle
import requests
import socket

from pypaths import astar
from time import sleep

# Possible modes
QUEUE_CONTROL = 0
MANUAL_CONTROL = 1
A_STAR = 2
CELEBRATE = 3

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
BASE_URL = "http://bigcat.fhsu.edu/newmedia/projects/stacks/robotLocateItem.php?call="

# 
ROBOT_SUCCESS_MSG = ("Directions completed.")
ROBOT_FAILURE_MSG = ("Direction completion failed.")

# Socket connections require a string to be sent when the connection ends
DISCONNECT_MESSAGE = "DISCONNECT"

mode = 2

# What direction should the robot expect to face when first starting in relation to the grid?
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
        raw_target_book_id = raw_input("target book id: ")
        target_book_id = raw_target_book_id.replace(" ", "+")

        complete_url = BASE_URL + target_book_id

        r = requests.get(complete_url)

        target_node_id = int(r.content)
        if target_node_id < 1:
            print("Invalid Target Node ID")

        else:
            target_node = VALID_NODES[target_node_id]

    return(target_node)


# Replacement for default "grid_neighbors" function that comes with the pypaths library
# Follows the same format of the original function
# Takes in a height and width, which correspond to the dimensions of the grid being used
def grid_neighbors(height, width):
    def func(coord):
        # Default values for node with four neighbors
        neighbor_list = [(coord[X], coord[Y] + 1),
                         (coord[X], coord[Y] - 1),
                         (coord[X] + 1, coord[Y]),
                         (coord[X] - 1, coord[Y])]

        # Checks if the node is in an even row and updates its neighbors accordingly
        if coord[Y] % 2 == 0:
            del neighbor_list[3]
            del neighbor_list[2]
            
            if coord[Y] <= 0:
                del neighbor_list[1]

            if coord[Y] + 1 >= height:
                del neighbor_list[0]

        # Ensures all coords are within grid
        return [c for c in neighbor_list
                if c != coord
                and c[0] >= 0 and c[0] < width
                and c[1] >= 0 and c[1] < height]

    return func


# Takes a starting node and ending node, calculates a path between the two points, and returns a list of coordinates the path goes through
def find_path(current_node, target_node):
    finder = astar.pathfinder(neighbors = grid_neighbors(GRID_HEIGHT, GRID_WIDTH))
    path_info = finder(current_node, target_node)

    return(path_info)

# Takes a turn direction and an old orientation, determines the new orientation, and returns the new orientation
def update_orientation(turn_direction, orientation):
    # All orientation constants are stored as ints ranging from 0 to 3.
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


# Takes the length of the path in nodes and a list of all the path coordinates and generates a list of turning directions by utilizing the current orientation
def path_to_directions(path_length, path_coord):
    global orientation

    # direction_queue is the list of turning directions which eventually gets sent to the robot
    direction_queue = []

    # Converts each coordinate into a turning direction that robot can use
    for i in range(path_length):
        # need to go east in the grid
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

        # need to go west in the grid
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

        # need to go north in the grid
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

        # need to go south in the grid
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

        # updates orientation to represent the robot after completing the turn
        orientation = update_orientation(turn_direction, orientation)

        # adds the turn direction to the list of directions the robot will be sent
        direction_queue.append(turn_direction)

    return(direction_queue)


def a_star(current_node):
    # if the robot is home, it needs to be given a destination
    if current_node == HOME_NODE:
        target_node = get_target_node()

    # if the robot is not home, it should go home
    else:
        target_node = HOME_NODE

    # retrieves the length of the path in nodes between the current node and target node, as well as a list of coordinates the path goes through
    path_info = find_path(current_node, target_node)

    path_length = path_info[0]
    path_coord = path_info[1]
    
    current_node = path_coord[path_length]

    # converts the list of coordinates to a list of turn directions
    direction_queue = path_to_directions(path_length, path_coord)
    print(direction_queue)

    return(direction_queue, current_node)

# connects to the robot
socket_connection.connect((HOST_IP, PORT))


# main loop
while True:
    # provide the robot with a list of manually-typed directions
    # it is up to the user to ensure the directions are possible and the robot reaches its destination
    if mode == QUEUE_CONTROL:
        directions = queue_control()
        directions.append(QUEUE_CONTROL)
        send_data(directions, socket_connection)

    # drive using W, A, and D keys
    elif mode == MANUAL_CONTROL:
        manual_control()

    # goes to a user-given target node and then returns back to its starting location
    elif mode == A_STAR:
        directions, current_node = a_star(HOME_NODE)
        directions.append(A_STAR)
        send_data(directions, socket_connection)

        print("Waiting for robot to reach destination.")
        ser_response_msg = socket_connection.recv(1024)
        response_msg = pickle.loads(ser_response_msg)

        if response_msg == ROBOT_FAILURE_MSG:
            print("Robot failed. Please retrieve the robot and return it to its home.")
            exit()

        else:
            print("Robot reached destination.")

            send_data(CELEBRATE)

            print("Waiting for robot to complete celebration.")
            ser_response_msg = socket_connection.recv(1024)
            response_msg = pickle.loads(ser_response_msg)

            if response_msg == ROBOT_FAILURE_MSG:
                print("Robot failed. Please retrieve the robot and return it to its home.")
                exit()

            else:
                print("Robot completed celebration. Returning home.")

                directions, current_node = a_star(current_node)
                directions.append(A_STAR)
                send_data(directions, socket_connection)

                print("Waiting for robot to reach destination.")

                ser_response_msg = socket_connection.recv(1024)
                response_msg = pickle.loads(ser_response_msg)

                if response_msg == ROBOT_FAILURE_MSG:
                    print("Robot failed. Please retrieve the robot and return it to its home.")
                    exit()
                
                else:
                    print("Robot returned home.")


    else:
        print("NOT A VALID MODE")
        print("Exiting.")
        socket_connection.send_all(DISCONNECT_MESSAGE)
        exit()
