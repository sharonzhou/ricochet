from collections import deque, defaultdict
import math, time
from render import print_board
from configs import *

def extremes(current, arr):
    """Find the highest and lowest available spots, 
    given current value and array of obstacles.
    returns (up, down) available locations"""
    up = BOARD_SIZE 
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

def get_next_states(robot_name, moves, state, blacklist):
    """packages next moves into actual states.
    robot_name: which robot we're moving.
    moves: a tuple of move coords that are possible
    state: current state vector.
    blacklist: don't send a robot to a location that's been sufficiently explored"""
    next_states = []
    for coord in moves:  # new coordinates for the moved robot
        
        # ignore moves that are stuck in the same place
        if coord == state["robots"][robot_name]:
            continue
        # ignore moves that bring us back to the robot's previous location
        elif state["prev_state"] is not None and coord == state["prev_state"]["robots"][robot_name]:
            continue
        # ignore moves that bring us to a very explored location
        elif blacklist[robot_name][coord] > blacklist["limit"]:
            continue
        # let's try it!
        else:
            blacklist[robot_name][coord] += 1

            # create a new state to add to the queue
            s = {}
            s["robots"] = state["robots"].copy()
            s["robots"][robot_name] = coord
            s["cost"] = state["cost"] + 1
            s["prev_state"] = state
            next_states.append(s)
    return next_states

def get_robot_moves(robot_name, state, walls=global_walls):
    """returns all possible next moves for the given robot.
    robot_name: a string name of a robot.
    state: a state object
    returns: tuples of coords that robot can move to. (up, down, right, left)"""
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
    """Checks if the current state wins"""
    return state["robots"][robot_name] == goal

def print_path(state, robot_name, goal=None):
    """Display all the states along the path we took"""
    count = 0
    while state is not None:
        print_board(state, global_walls, goal)
        state = state["prev_state"]
        count += 1
    print("number of moves: {}".format(count))
    
def solve(start_state, goal_robot_name, goal):
    """find the shortest number of moves!"""
    q = deque()  # a queue to keep track of our rough BFS
    q.append(start_state)

    # for reporting
    cost = 0
    t0 = time.time()

    # we use a global blacklist to stop ourselves from visiting the same point too many times
    blacklist = {name: defaultdict(int) for name in start_state["robots"]}
    blacklist["limit"] = 20000
    
    while True:
        state = q.popleft()
        
        if DEBUG:
            new_cost = state["cost"]
            if new_cost > cost:
                cost = new_cost
                print("step: {} time: {}".format(cost, time.time() - t0))

        next_states = []
        for robot_name in state["robots"]:
            moves = get_robot_moves(robot_name, state)
            next_states.extend(get_next_states(robot_name, moves, state, blacklist))
        
        for next_state in next_states:
            if win(next_state, goal_robot_name, goal):
                return next_state
            q.append(next_state)
        
def test_solve():
    goal = (3,1)
    state = {"robots": starting_robots, "cost":0, "prev_state":None}
    robot_name = "red"
    winning_state = solve(state, robot_name, goal)

    print_path(winning_state, robot_name, goal)
    print("we won huzzah!")
            
def test_get_robot_moves():
    robot_name = "red"
    walls = [(3.5,1)]
    state = {"robots":{"red": (1,1), "green": (1,3)}, "cost":0, "prev_state":None}
    res = get_robot_moves(robot_name, state, walls=walls)
    assert res == ((1, 2), (1, 0), (3, 1), (0, 1)), "got {}".format(res)
    print("robot move still works ;)")
    
def test_print_board():
    state = {"robots":starting_robots, "cost":0, "prev_state":None}
    print_board(state, global_walls, (5,5))


test_solve()
# test_print_board()
# test_get_robot_moves()

