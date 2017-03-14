import pickle
import socket

A_STAR = 0
MANUAL_CONTROL = 1

ROBOT = 1

HOST_IP = "209.114.104.54"
PORT = 9999

TRUE_UP = 0
TRUE_DOWN = 1
TRUE_LEFT = 2
TRUE_RIGHT = 3

STRAIGHT = 0
LEFT = 1
RIGHT = 2

START_X = 3
START_Y = 2
grid = [[0, 0, 0],
        [0, 0, 1]]

START_ORIENTATION = TRUE_UP
DISCONNECT_MESSAGE = "DISCONNECT"

socket_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

class Robot_Handler:
        def __init__(self, grid):
                self.mode = MANUAL_CONTROL

                self.grid = grid
                self.grid_x = len(grid[0])
                self.grid_y = len(grid)

                for y in range(self.grid_y):
                        for x in range(self.grid_x):
                                node_value = self.grid[y][x]

                                if node_value == ROBOT:
                                        self.x = x
                                        self.y = y

                self.true_orientation = START_ORIENTATION

                self.possible_orientations = [TRUE_UP, TRUE_DOWN, TRUE_LEFT, TRUE_RIGHT]

        def get_possible_orientations(self):
                self.possible_orientations = [TRUE_UP, TRUE_DOWN, TRUE_LEFT, TRUE_RIGHT]
                if self.y == 0:
                        del self.possible_orientations[0]
                        
                elif self.y == 1:
                        del self.possible_orientations[1]
                        
                elif self.x == 0:
                        del self.possible_orientations[2]

                elif self.x == 2:
                        del self.possible_orientations[3]


                if self.true_orientation == TRUE_UP:
                        del self.possible_orientations[1]

                elif self.true_orientation == TRUE_DOWN:
                        del self.possible_orientations[0]

                elif self.true_orientation == TRUE_LEFT:
                        del self.possible_orientations[3]

                elif self.true_orientation == TRUE_RIGHT:
                        del self.possible_orientations[2]


        def get_input(self):
                user_input = False

                while not user_input:
                        user_input = raw_input("DIRECTION (u, d, l, r): ")
                        
                        if user_input == "u":
                                user_input = TRUE_UP

                        elif user_input == "d":
                                user_input = TRUE_DOWN

                        elif user_input == "l":
                                user_input = TRUE_LEFT

                        elif user_input == "r":
                                user_input = TRUE_RIGHT

                        #if user_input in self.possible_orientations:

                        else:
                                user_input = False
                                print("Cannot go that direction.")

                        self.true_goal = user_input


        def convert_true_to_relative(self):
                if self.true_orientation == self.true_goal:
                        self.relative_goal = STRAIGHT

                elif self.true_orientation == TRUE_UP:
                        if self.true_goal == TRUE_LEFT:
                                self.relative_goal = LEFT

                        else:
                                self.relative_goal = RIGHT

                elif self.true_orientation == TRUE_DOWN:
                        if self.true_goal == TRUE_LEFT:
                                self.relative_goal = RIGHT

                        else:
                                self.relative_goal = LEFT

                elif self.true_orientation == TRUE_LEFT:
                        if self.true_goal == TRUE_UP:
                                self.relative_goal = RIGHT

                        else:
                                self.relative_goal = LEFT

                elif self.true_orientation == TRUE_RIGHT:
                        if self.true_goal == TRUE_UP:
                                self.relative_goal = LEFT

                        else:
                                self.relative_goal = RIGHT


        def update_location(self):
                if self.true_goal == TRUE_UP:
                        self.grid[self.y][self.x] = 0
                
                        self.y -= 1
                        print(self.x, self.y)
                        self.grid[self.y][self.x] = 1

                elif self.true_goal == TRUE_DOWN:
                        self.grid[self.y][self.x] = 0

                        self.y += 1
                        print(self.x, self.y)
                        self.grid[self.y][self.x] = 1

                elif self.true_goal == TRUE_LEFT:
                        self.grid[self.y][self.x] = 0

                        self.x -= 1
                        print(self.x, self.y)
                        self.grid[self.y][self.x] = 1

                elif self.true_goal == TRUE_RIGHT:
                        self.grid[self.y][self.x] = 0

                        self.x += 1
                        print(self.x, self.y)
                        self.grid[self.y][self.x] = 1


        def update_orientation(self):
                self.true_orientation = self.true_goal


        def run(self):
                if self.mode == MANUAL_CONTROL:
                        self.get_possible_orientations()
                        self.get_input()
                        self.convert_true_to_relative()
                        self.update_location()
                        self.update_orientation()
                        print(self.grid)


socket_connection.connect((HOST_IP, PORT))
connected = True

robot = Robot_Handler(grid)
while connected:
        #robot.run()

        turns = []
        for i in range(10):
                turn_direction = raw_input("left, right, straight: ")
                turns.append(turn_direction)
                

        data = turns 
        data = pickle.dumps(data)

        socket_connection.sendall(data)

        while not socket_connection.recv(1024):
                print("Waiting for response...")

        print("Response recieved!")


socket_connection.send_all(DISCONNECT_MESSAGE)
socket_connection.close()
