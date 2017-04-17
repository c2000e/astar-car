from pypaths import astar

X = 0
Y = 1

NORTH = 0
EAST = 1
SOUTH = 2
WEST = 3

LEFT = "left"
STRAIGHT = "straight"
RIGHT = "right"

GRID_HEIGHT = 6
GRID_WIDTH = 6

orientation = NORTH
starting_node = (0, 0)

possible_nodes = []
for y in range(GRID_HEIGHT):
    for x in range(GRID_WIDTH):
        node_coord = (x, y)
        possible_nodes.append(node_coord)


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

starting_node = target_node
        
print(path)
print(direction_queue)
