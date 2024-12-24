"""
6.1010 Lab:
Snekoban Game
"""

# import json # optional import for loading test_levels
# import typing # optional import
# import pprint # optional import

# NO ADDITIONAL IMPORTS!


DIRECTION_VECTOR = {
    "up": (-1, 0),
    "down": (+1, 0),
    "left": (0, -1),
    "right": (0, +1),
}


def make_new_game(level_description):
    """
    Given a description of a game state, create and return a game
    representation of your choice.

    The given description is a list of lists of lists of strs, representing the
    locations of the objects on the board (as described in the lab writeup).

    For example, a valid level_description is:

    [
        [[], ['wall'], ['computer']],
        [['target', 'player'], ['computer'], ['target']],
    ]

    The exact choice of representation is up to you; but note that what you
    return will be used as input to the other functions.
    """
    ## return tuple of four things:
    ## set of wall coordinates { (x, y) }
    ## set of target coordinates { (x, y) }
    ## set of computer coordinates { (x, y) }
    ## current player coordinates (x, y)
    ## dimensions of game board (for converting back later): (m, n)

    ## first create sets, then convert later
    walls = set()
    targets = set()
    computers = set()
    player = ()
    dimensions = (len(level_description), len(level_description[0]))

    ## iterate through level description to concurrently update all lists
    rows = len(level_description)
    cols = len(level_description[0])
    for i in range(rows):
        for j in range(cols):
            cur_square = level_description[i][j]
            for cur_str in cur_square:
                if cur_str == "wall":
                    walls.add((i, j))
                elif cur_str == "target":
                    targets.add((i, j))
                elif cur_str == "computer":
                    computers.add((i, j))
                elif cur_str == "player":
                    player = (i, j)

    ## we would like everything to be immutable given conditions of step_game
    frozen_walls = frozenset(walls)
    frozen_targets = frozenset(targets)
    frozen_computers = frozenset(computers)
    wrapper = (frozen_walls, frozen_targets, frozen_computers, player, dimensions)
    return wrapper


def victory_check(game):
    """
    Given a game representation (of the form returned from make_new_game),
    return a Boolean: True if the given game satisfies the victory condition,
    and False otherwise.
    """

    
    targets = game[1]
    computers = game[2]
    ## check if target(s) exists
    if not targets:
        return False
    ## check if every target is covered by a computer
    for target_coord in targets:
        if target_coord not in computers:
            return False
    return True


def step_game(game, direction):
    """
    Given a game representation (of the form returned from make_new_game),
    return a game representation (of that same form), representing the
    updated game after running one step of the game.  The user's input is given
    by direction, which is one of the following:
        {'up', 'down', 'left', 'right'}.

    This function should not mutate its input.
    """
    ## unpack game board
    (walls, targets, computers, player, dimensions) = game

    ## helper function to update coordinates
    def update_coord(coord: tuple, direction: str) -> tuple:
        return tuple(map(lambda i, j: i + j, coord, DIRECTION_VECTOR[direction]))

    ## new desired position
    new_player = update_coord(player, direction)

    ## check if bumps into wall
    if new_player in walls:
        return game

    updated_computers = set(computers)
    ## check if bumps into computer
    if new_player in computers:
        new_computer = update_coord(new_player, direction)
        ## if so, see if computer bumps into computer or wall
        if new_computer in computers or new_computer in walls:
            return game
        ## if not, move computer
        updated_computers.remove(new_player)
        updated_computers.add(new_computer)
    ## move snake
    return (walls, targets, frozenset(updated_computers), new_player, dimensions)


def dump_game(game):
    """
    Given a game representation (of the form returned from make_new_game),
    convert it back into a level description that would be a suitable input to
    make_new_game (a list of lists of lists of strings).

    This function is used by the GUI and the tests to see what your game
    implementation has done, and it can also serve as a rudimentary way to
    print out the current state of your game for testing and debugging on your
    own.
    """
    ## unpack game board
    (walls, targets, computers, player, dimensions) = game
    rows = dimensions[0]
    cols = dimensions[1]
    board = [[[] for j in range(cols)] for i in range(rows)]
    
    ## helper function to populate board given object name
    ##      and frozenset of position coordinates
    def populate_board(board, name: str, positions: frozenset):
        for position in positions:
            board[position[0]][position[1]].append(name)

    populate_board(board, 'wall', walls)
    populate_board(board, 'target', targets)
    populate_board(board, 'computer', computers)
    board[player[0]][player[1]].append('player')
    return board


def solve_puzzle(game):
    """
    Given a game representation (of the form returned from make_new_game), find
    a solution.

    Return a list of strings representing the shortest sequence of moves ("up",
    "down", "left", and "right") needed to reach the victory condition.

    If the given level cannot be solved, return None.
    """

    ## unpack game board
    (walls, targets, computers, player, dimensions) = game

    ## start state: tuple of computer and player positions
    start = (computers, player)

    ## let path be tuple of strings (moves), 
    #        ---> modify if too space/time expensive
    ## agenda is tuple of (moves, cur state)
    agenda = [ ((), start) ]
    visited = {start}        

    while agenda:
        cur = agenda.pop(0)
        cur_path = cur[0]
        cur_comp = cur[1][0]
        cur_player = cur[1][1]

        ## re-wrap
        cur_game = (walls, targets, cur_comp, cur_player, dimensions)

        if victory_check(cur_game):
            return cur_path

        for direction in ["up", "down", "left", "right"]:
            new_game = step_game(cur_game, direction)
            ## extract state
            new_path = cur_path + (direction, )
            new_state = (new_game[2], new_game[3])
            if new_state not in visited:
                agenda.append((new_path, new_state))
                visited.add(new_state)
    return None


if __name__ == "__main__":
    
    pass
