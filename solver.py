from collections import deque
import math, pprint


pp = pprint.PrettyPrinter(indent=4)
MAX = 15

# x, y tuples
walls = [
    (3.5, 0),  # all vertical walls
    (13.5, 0),
    (10.5, 1),
    (3.5, 2),
    (1.5, 3),
    (14.5, 3),
    (5.5, 4),
    (3.5, 5),
    (10.5, 5),
    (11.5, 6),
    (6.5, 7),
    (8.5, 7),
    (6.5, 8),
    (8.5, 8),
    (1.5, 9),
    (11.5, 9),
    (5.5, 10),
    (3.5, 11),
    (9.5, 11),
    (14.5, 12),
    (7.5, 13),
    (4.5, 14),
    (10.5, 14),
    (2.5, 15),
    (8.5, 15),
    
    (0, 5.5),
    (0, 11.5),
    (1, 9.5),
    (2, 2.5),
    (3, 4.5),
    (3, 10.5),
    (4, 2.5),
    (5, 4.5),
    (5, 13.5),
    (6, 10.5),
    (7, 6.5),
    (7, 8.5),
    (7, 12.5),
    (8, 6.5),
    (8, 8.5),
    (9, 10.5),
    (10, 4.5),
    (11, 0.5),
    (11, 14.5),
    (12, 6.5),
    (12, 8.5),
    (14, 3.5),
    (14,12.5),
    (15,5.5),
    (15, 13.5)
]

# x, y, robot_color tuples
starting_robots = {
    "red": (0, 0),
    "green": (2,3),
    "blue": (15,15)
}

def render(name):
    # color defs
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YEL = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    
    if name == "green":
        color = GREEN
    elif name == "red":
        color = RED
    else:
        color = BLUE
        
    return color + name[0:2].upper() + ENDC

def print_board(state, goal=None):
    row1 = list("..  " * (MAX + 1))
    row2 = list("    " * (MAX + 1))
    board = [row1, row2] * (MAX + 1)
    
    board = [["----"] * (MAX + 1)]
    for _ in range(MAX + 1):
        # create row to hold robots
        row = ["||"]
        for _ in range(MAX + 1):
            row.extend(["..", "  "])
        row[-1] = "||"
        board.append(row)
        
        # create row to hold walls
        row = ["||"]
        for _ in range(MAX + 1):
            row.extend(["  ", "  "])
        row[-1] = "||"
        board.append(row)
    board.append(["----"] * (MAX + 1))
        
    # add walls
    for x, y in walls:
        if x != int(x):
            wall = "||"
        else:
            wall = "--"
        board[int(y*2 + 1)][int(x*2 + 1)] = wall
        
    # add goal
    if goal is not None:
        x, y = goal
        board[int(y*2 + 1)][int(x*2 + 1)] = "**"
        
    # add robots
    for name, (x, y) in state["robots"].items():
        board[int(y*2 + 1)][int(x*2 + 1)] = render(name)
        
    
    board.reverse()  # because list indexing is upside down
    for row in board:
        print("".join(row))
    

def extremes(current, arr):
    # start with where walls are
    up = MAX + 1
    down = -1
    for v in arr:
        if v > current and v < up:
            up = v
        elif v < current and v > down:
            down = v
    
    # fix rounding of walls/robots
    up = math.ceil(up) - 1  # actual places we can go are off by one
    down = math.floor(down) + 1
    return up, down

def get_next_states(robot_name, state):
    """packages next moves into actual states"""
    moves = get_robot_moves(robot_name, state)
    next_states = []
    for coord in moves:  # new coordinates for the moved robot
        s = {}
        s["robots"] = state["robots"].copy()
        s["robots"][robot_name] = coord
        s["cost"] = state["cost"] + 1
        s["prev_state"] = state
        next_states.append(s)
    return next_states

# get_robot_moves
def get_robot_moves(robot_name, state):
    """returns all possible next moves for the given robot.
    robot_name: a string name of a robot.
    state: a state object
    returns: tuples of coords that robot can move to"""
    current_x, current_y = state["robots"][robot_name]
    
    # find walls and robots with same x coord or y coord
    xs, ys = [], []
    for x, y in walls + list(state["robots"].values()):
        if x == current_x:
            ys.append(y)
        if y == current_y:
            xs.append(x)        

    # find closest walls/robots in all directions
    up_y, down_y = extremes(current_y, ys)
    right_x, left_x = extremes(current_x, xs)
    
    # create record tuples (up, down, right, left)
    return ((current_x, up_y),
            (current_x, down_y),
            (right_x, current_y),
            (left_x, current_y))

def win(state, robot_name, goal):
    return state["robots"][robot_name] == goal

def print_path(state, robot_name, goal=None):
    path = [state["robots"][robot_name]]
    while state["prev_state"] is not None:
        print_board(state, goal)
        state = state["prev_state"]
        path.append(state["robots"][robot_name])
    print_board(state, goal)
    pp.pprint(list(reversed(path)))
    
    
def solve(start_state, goal_robot_name, goal):
    """find the shortest number of moves!"""
    q = deque()
    q.append(start_state)
    
    while True:
        state = q.popleft()
        next_states = []
        for robot_name in state["robots"]:
            next_states.extend(get_next_states(robot_name, state))
        
        for next_state in next_states:
            if win(next_state, goal_robot_name, goal):
                pp.pprint("we won huzzah!")
                print_path(next_state, robot_name, goal)
                return
            q.append(next_state)
        
def test_solve():
    goal = (5,4)
    state = {"robots":{"red": (0,0), "green":(6,3), "blue":(1,6)}, "cost":0, "prev_state":None}
    robot_name = "red"
    solve(state, robot_name, goal)
            
def test_get_robot_moves():
    robot_name = "red"
    state = {"robots":{"red": (1,1)}, "cost":0, "prev_state":None}
    res = get_robot_moves(robot_name, state)
    assert res == ((1, 2), (1, 0), (3, 1), (0, 1))
    print("robot move still works ;)")

def test_get_next_states():
    robot_name = "red"
    state = {"robots":{"red": (1,1)}, "cost":0, "prev_state":None}
    res = get_next_states(robot_name, state)
    pp.pprint(res)
    
def test_print_board():
    state = {"robots":starting_robots, "cost":0, "prev_state":None}
    print_board(state, (5,5))

# test_print_board()
test_solve()
# test_get_next_states()
# test_get_robot_moves()

