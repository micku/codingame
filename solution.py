import sys
import math

WALLS = '*'
MOVES = {
    'UP': (0, -1),
    'RIGHT': (1, 0),
    'DOWN': (0, 1),
    'LEFT': (-1, 0),
}
MAX_DEPTH = 9

# w: width of the board
# h: height of the board
# player_count: number of players (2 or 3)
# my_id: id of my player (0 = 1st player, 1 = 2nd player, ...)
w, h, player_count, my_id = [int(i) for i in input().split()]
opponent_id = [i for i in range(player_count) if i != my_id][0]
win_obj = (8 if my_id == 0 else 0, None)

winning_positions = {
    0: [(w-1, i) for i in range(h)],
    1: [(0, i) for i in range(h)],
}

turn = 0

### Pathfinding
class Board:
    def __init__(self, w=None, h=None, board=None):
        if board is not None:
            self.clone(board)
        else:
            self.the_map = [[' ' for x in range((w*2)-1)] for y in range((h*2)-1)]
            for y in range(len(self.the_map)):
                for x in range(len(self.the_map[y])):
                    if y % 2 == 1:
                        self.the_map[x][y] = '-'
                    elif x % 2 == 1:
                        self.the_map[x][y] = '|'

    def clone(self, board):
        self.the_map = [y[:] for y in board.the_map]
    
    def shortest_path(self, pos, goal): # A*
        op = set()
        cl = set()
        
        starting = Node((None, pos))
        op.add(starting)
        
        while len(op) > 0:
            q = min(op, key=lambda x: x.f)
            op.remove(q)
            
            for space in self.possible_moves(q.pos()):
                successor = Node(space, parent=q, h=self.heuristic_distance(space[1], goal))
                
                if space[1] == goal:
                    return successor

                same_successors = list(filter(lambda x: x.pos() == space[1], op | cl))
                if not same_successors or min(same_successors, key=lambda x: x.f).f >= successor.f:
                    op.add(successor)
            
            cl.add(q)
    
    def heuristic_distance(self, space, goal): # TODO
        return math.sqrt((space[0] - goal[0])**2 + (space[1] - goal[1])**2)

    ### Finds all possible moves in the map
    def is_movement_valid(self, pos, direction):
        new_pos = (pos[0] + direction[0], pos[1] + direction[1])
        new_map_pos = ((pos[0]*2)+direction[0], (pos[1]*2)+direction[1])
    
        return new_pos[0] >= 0 \
            and new_pos[1] >= 0 \
            and new_pos[0] < w \
            and new_pos[1] < h \
            and self.the_map[new_map_pos[0]][new_map_pos[1]] != WALLS, new_pos

    def possible_moves(self, pos):
        for k, v in MOVES.items():
            is_valid, new_pos = self.is_movement_valid(pos, v)
            if is_valid:
                yield (k, new_pos)
    
    ### Board construction
    def add_wall(self, pos, wall_orientation):
        wall_x, wall_y = pos
        x = wall_x*2 if wall_orientation == 'H' else (wall_x*2)-1
        y = wall_y*2 if wall_orientation == 'V' else (wall_y*2)-1
        
        for i in range(3):
            self.the_map[x+(i if wall_orientation == 'H' else 0)][y+(i if wall_orientation == 'V' else 0)] \
                = WALLS

    ### Utilities
    def __repr__(self):
        output = []
        for y in zip(*self.the_map):
            output.append(''.join([str(x) for x in y]))
        return '\n'.join(output)



class Node:
    parent = None # Type Node
    x, y = 0, 0
    f, g, h = 0.0, 0.0, 0.0
    
    def __init__(self, space, parent=None, h=None):
        self.direction = space[0]
        self.x, self.y = space[1]
        self.parent = parent
        
        self.g = self.__calc_g()
        self.h = h or 0.0
        self.f = self.__calc_f()
    
    def __calc_g(self):
        return self.parent.g + 1.0 if self.parent else 0.0
    
    def __calc_f(self):
        return self.g + self.h
    
    def pos(self):
        return (self.x, self.y)
        
    def first_move(self):
        first = self
        while first.parent and first.parent.direction:
            first = first.parent
        return first


while True:
    board = Board(w, h)

    players = {}
    for i in range(player_count):
        # x: x-coordinate of the player
        # y: y-coordinate of the player
        # walls_left: number of walls available for the player
        x, y, walls_left = [int(j) for j in input().split()]
        players[i] = (x, y, walls_left)
    
    wall_count = int(input())  # number of walls on the board
    for i in range(wall_count):
        # wall_x: x-coordinate of the wall
        # wall_y: y-coordinate of the wall
        # wall_orientation: wall orientation ('H' or 'V')
        wall_x, wall_y, wall_orientation = input().split()
        wall_x = int(wall_x)
        wall_y = int(wall_y)
        
        board.add_wall((wall_x, wall_y), wall_orientation)

    my_position = (players[my_id][0], players[my_id][1])

    # Go in the winning direction as first action, the board is empty!
    goal = (8, my_position[1])
    shortest_path = board.shortest_path(my_position, goal)
    first_move = shortest_path.first_move()

    print(repr(board), file=sys.stderr)
    
    # action: LEFT, RIGHT, UP, DOWN or "putX putY putOrientation" to place a wall
    print(first_move.direction)

turn += 1
    
