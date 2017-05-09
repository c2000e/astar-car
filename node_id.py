import requests

# Dimensions of grid
GRID_HEIGHT = 6
GRID_WIDTH = 6

# List of all nodes within the grid dimensions
VALID_NODES = []
for y in range(GRID_HEIGHT):
    for x in range(GRID_WIDTH):
        node_coord = (x, y)
        VALID_NODES.append(node_coord)

# Partial URL for library database
BASE_URL = "http://bigcat.fhsu.edu/newmedia/projects/stacks/robotLocateItem.php?call="

raw_target_book_id = raw_input("target stack id: ")
target_book_id = raw_target_book_id.replace(" ", "+")

complete_url = BASE_URL + target_book_id

r = requests.get(complete_url)

target_node_id = int(r.content)
print(target_node_id)
if target_node_id < 1:
    print("Invalid Target Node ID")

else:
    target_node = VALID_NODES[target_node_id]
    print(target_node)
