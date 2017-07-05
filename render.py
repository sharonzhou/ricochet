from configs import BOARD_SIZE

def render_item(name):
    """Print a robot or goal name and color"""
    # color defs
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YEL = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    CYAN  = "\033[1;36m"

    if name == "goal":
        color = CYAN
    elif name == "green":
        color = GREEN
    elif name == "red":
        color = RED
    elif name == "blue":
        color = BLUE
    elif name == "yellow":
        color = YEL
    else:
        color = ""
        
    return color + name[0:2].upper() + ENDC

def get_empty_board(n):
    """Render empty board, to add stuff to later"""
    board = []
    for y in range(BOARD_SIZE * 2 - 1):
        board.append([])
        for x in range(BOARD_SIZE * 2 - 1):
            if x % 2 == 0 and y % 2 == 0:
                board[y].append(" ·")  # mark a spot for a robot
            else:
                board[y].append("  ")

    return board

def draw_frame(board):
    """Draws a nice pipe boarder around a board"""
    n_rows = len(board)
    n_cols = len(board[0])
    top_row = [" ┌"] + ["——"] * n_cols + ["—┐"]
    bottom_row = [" └"] + ["——"] * n_cols + ["—┘"]

    new_board = []
    for row in board:
        new_row = [" |"] + row + [" |"]
        new_board.append(new_row)
    return [top_row] + new_board + [bottom_row]

def draw_corners(board):
    """Inserts fancy corner pipe characters"""
    for y in range(2, len(board)-2):
        for x in range(2, len(board[0])-2):
            if board[y+1][x] == " │" and board[y][x+1] == "——":
                board[y][x] = " ┌"
            elif board[y-1][x] == " │" and board[y][x+1] == "——":
                board[y][x] = " └"
            elif board[y+1][x] == " │" and board[y][x-1] == "——":
                board[y][x] = "—┐"
            elif board[y-1][x] == " │" and board[y][x-1] == "——":
                board[y][x] = "—┘"

    # handle frames as special cases
    for y in range(1, len(board)-1):
        if board[y][-2] == "——":
            board[y][-1] = "—┤"
        if board[y][1] == "——":
            board[y][0] = " ├"

    for x in range(1, len(board[2])-1):
        if board[-2][x] == " │":
            board[-1][x] = "—┴"
        if board[1][x] == " │":
            board[0][x] = "—┬"

    return board


def print_board(state, walls, goal=None):
    """Draw the board with ascii art in a pretty way.
    There is a 'location' every 0.5 spacing.
    Each 'location' is rendered with two chars.
    # Until the very end, this is an array of arrays, not strings
    # also note that this is rendered upside down, then flipped at the end"""
    board = get_empty_board(BOARD_SIZE)
        
    # add walls
    for x, y in walls:
        if x != int(x):  # change render based on whether x or y is between ints
            wall = " │"
        else:
            wall = "——"
        board[int(y * 2)][int(x * 2)] = wall
        
    # add goal
    if goal is not None:
        x, y = goal
        board[int(y * 2)][int(x * 2)] = render_item("goal")
        
    # add robots
    for name, (x, y) in state["robots"].items():
        board[int(y * 2)][int(x * 2)] = render_item(name)
        
    board.reverse()  # because list indexing is upside down
    board = draw_frame(board)
    board = draw_corners(board)

    # combine into nice string and print
    for row in board:
        print("".join(row))
