import requests
from pypaths import astar

# Dimensions of grid
GRID_HEIGHT = 6
GRID_WIDTH = 6

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

orientation = NORTH

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

while True:
    directions, current_node = a_star(HOME_NODE)
    directions, current_node = a_star(current_node)
