from collections import deque, defaultdict
import math, time
from render import print_board
from configs import *

# State Vector
# dict(robots=dict(color=(x,y), cost=0, prev_state=None))

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
    up = math.ceil(up)
    down = math.floor(down)
    return up, down

extreme_cache = None
def cache_wall_extremes(walls=global_walls):
    """For each location on the board, create a list of the extreme wall positions"""
    global extreme_cache
    extreme_cache = {}
    for current_x in range(BOARD_SIZE):
        for current_y in range(BOARD_SIZE):

            xs, ys = [], []
            for x, y in walls:
                if x == current_x:
                    ys.append(y)
                if y == current_y:
                    xs.append(x)        

            # find closest walls/robots in all directions
            up_y, down_y = extremes(current_y, ys)
            right_x, left_x = extremes(current_x, xs)

            extreme_cache[(current_x, current_y)] = (up_y, down_y, right_x, left_x)

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
    if extreme_cache is None:
        cache_wall_extremes()

    up_y, down_y, right_x, left_x = extreme_cache[(current_x, current_y)]
    xs, ys = [right_x, left_x], [up_y, down_y]  # add wall extremes to list
    to_check = list(state["robots"].values())  # then check over robots

    for x, y in to_check:
        if x == current_x:
            ys.append(y)
        if y == current_y:
            xs.append(x)        

    # find closest walls/robots in all directions
    up_y, down_y = extremes(current_y, ys)
    right_x, left_x = extremes(current_x, xs)
    
    # create record tuples (up, down, right, left)
    return ((current_x, up_y - 1),  # need to go off by 1, for places robot can actually go
            (current_x, down_y + 1),
            (right_x - 1, current_y),
            (left_x + 1, current_y))

def win(state, robot_name, goal):
    """Checks if the current state wins"""
    return state["robots"][robot_name] == goal

def print_path(state, robot_name, goal=None):
    """Display all the states along the path we took"""
    count = 0
    while state is not None:
        print_board(state["robots"], global_walls, goal)
        state = state["prev_state"]
        count += 1
    print("number of moves: {}".format(count))
    
def solve_case(start_state, goal_robot_name, goal, movable_robots=None, blacklist_limit=20, cost_limit=20):
    """find the shortest number of moves to solve, given a number of options.
    start_state: initial conditions of board
    goal_robot_name: which robot we're trying to move
    goal: (x,y) of where to get it
    movable_robots: list of robot names we can move
    blacklist_limit: max times we'll look at once place
    cost_limit: max steps"""
    q = deque()  # a queue to keep track of our rough BFS
    q.append(start_state)

    # for reporting
    cost = 0
    t0 = time.time()

    # we use a global blacklist to stop ourselves from visiting the same point too many times
    blacklist = {name: defaultdict(int) for name in start_state["robots"]}
    blacklist["limit"] = blacklist_limit

    # which robots are we allowed to move?
    if movable_robots is None:
        movable_robots = start_state["robots"].keys()
    
    while len(q) > 0:
        state = q.popleft()

        if state["cost"] > cost_limit:
            return None
        
        if DEBUG:
            new_cost = state["cost"]
            if new_cost > cost:
                cost = new_cost
                print("step: {} time: {}".format(cost, time.time() - t0))

        next_states = []
        for robot_name in movable_robots:
            moves = get_robot_moves(robot_name, state)
            next_states.extend(get_next_states(robot_name, moves, state, blacklist))
        
        for next_state in next_states:
            if win(next_state, goal_robot_name, goal):
                return next_state
            q.append(next_state)

    # ran out of search options
    return None

def full_solve(start_state, goal_robot_name, goal):
    """Solves the board by calling solve_case many times with different paramters.
    1. only move the goal robot
    2. solve with all robots, low blacklist depth
    3. solve with all robots, high blacklist depth"""

    print("Trying to only move main robot")
    result = solve_case(start_state, goal_robot_name, goal, 
        movable_robots=[goal_robot_name],
        blacklist_limit=float('inf'),
        cost_limit=15)
    if result:
        return result

    print("moving all robots, with low blacklist limit")
    result = solve_case(start_state, goal_robot_name, goal, 
        movable_robots=None,
        blacklist_limit=20,
        cost_limit=15)
    if result:
        return result

    print("move 1 other robot at a time, low blacklist")
    other_robots = [rob for rob in start_state["robots"] if rob != goal_robot_name]
    for robot in other_robots:
        print("Trying {}".format(robot))
        result = solve_case(start_state, goal_robot_name, goal, 
            movable_robots=[goal_robot_name, robot],
            blacklist_limit=200,
            cost_limit=15)
        if result:
            return result


    print("move 1 other robot at a time")
    other_robots = [rob for rob in start_state["robots"] if rob != goal_robot_name]
    for robot in other_robots:
        print("Trying {}".format(robot))
        result = solve_case(start_state, goal_robot_name, goal, 
            movable_robots=[goal_robot_name, robot],
            blacklist_limit=2000,
            cost_limit=10)
        if result:
            return result

    print("moving all robots, with high blacklist limit")
    result = solve_case(start_state, goal_robot_name, goal, 
        movable_robots=None,
        blacklist_limit=2000,
        cost_limit=15)
    if result:
        return result


    return None
        
def test_solve_case():

    # cache_wall_extremes()
    goal = default_goal
    robot_name = default_robot
    state = {"robots": starting_robots, "cost":0, "prev_state":None}
    
    winning_state = solve_case(state, robot_name, goal, blacklist_limit=2000)
    if winning_state is not None:
        print_path(winning_state, robot_name, goal)
        print("we won huzzah!")
    else:
        print_path(state, robot_name, goal)
        print("did not win")
            
def test_get_robot_moves():
    robot_name = "red"
    walls = [(3.5,1)]
    state = {"robots":{"red": (1,1), "green": (1,3)}, "cost":0, "prev_state":None}
    cache_wall_extremes(walls)
    res = get_robot_moves(robot_name, state, walls=walls)
    assert res == ((1, 2), (1, 0), (3, 1), (0, 1)), "got {}".format(res)
    print("robot move still works ;)")
    
def test_print_board():
    print_board(starting_robots, global_walls, (5,5))

def test_full_solve():
    goal = default_goal
    robot_name = default_robot
    state = {"robots": starting_robots, "cost":0, "prev_state":None}
    
    winning_state = full_solve(state, robot_name, goal)
    if winning_state is not None:
        print_path(winning_state, robot_name, goal)
        print("we won huzzah!")
    else:
        print_path(state, robot_name, goal)
        print("did not win")


test_full_solve()
# test_solve_case()
# test_print_board()
# test_get_robot_moves()

