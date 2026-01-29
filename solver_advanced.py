# solver_advanced.py
# Advanced Sudoku Solver using MRV + LCV

from heuristics import mrv, lcv


def is_complete(grid):
    for r in range(9):
        for c in range(9):
            if grid[r][c] == 0:
                return False
    return True


def solve_advanced(grid):
    if is_complete(grid):
        return True

    cell = mrv(grid)
    if cell is None:
        return False  # dead end

    r, c = cell

    for value in lcv(grid, r, c):
        grid[r][c] = value
        if solve_advanced(grid):
            return True
        grid[r][c] = 0

    return False
