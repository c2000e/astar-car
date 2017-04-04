from pypaths import astar
finder = astar.pathfinder()

X = 0
Y = 1

NORTH = 0
EAST = 1
SOUTH = 2
WEST = 3

LEFT = "left"
STRAIGHT = "straight"
RIGHT = "right"

GRID_HEIGHT = 4
GRID_WIDTH = 6

orientation = NORTH
starting_node = (0, 0)

possible_nodes = []
for y in range(GRID_HEIGHT):
    for x in range(GRID_WIDTH):
        node_coord = (x, y)
        possible_nodes.append(node_coord)

target_node_id = -1
while target_node_id == -1:
    target_node_id = int(raw_input("target node [0 - 25]: "))
    if target_node_id <= 0:
        target_node_id = -1

    elif target_node_id > 23:
        if target_node_id == 24:
            target_node_id = 0
            #go_home()

        elif target_node_id == 25:
            target_node_id = 23
            #go_home()

        else:
            target_node_id = -1
            print("Invalid input.")

    else:
        print("Input accepted")
            

target_node = possible_nodes[target_node_id]

path = finder(starting_node, target_node)

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
        
print(path)
print(direction_queue)
