# Ricochet

## A terminal based solver for the game 'Ricochet Robots'!

![example](/board.png)

## Usage

`python3 solver.py`

Edit the robot locations, goal, and walls in `configs.py`

Robots and the goal have integer coordinates, and walls have non-integer coordinates. i.e. a wall with coordinates `(3.5, 0)` would block a robot moving from `(3, 0)` to `(4, 0)`.

## Overview

Ricochet Robots has a default branching factor of 16 (any of the 4 robots can move in any of the 4 directions each turn), making it very difficult to solve beyond 5 or 6 moves with a brute force breadth first search.

We prune repetitive states out of the search tree (i.e. a move of 0 distance up against a wall, or a move that goes right back to the previous state) add a global "blacklist" to stop robots from exploring locations that they have already explored a significant number of times.