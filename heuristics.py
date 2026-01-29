# heuristics.py
# Correct MRV and LCV heuristics for Sudoku

def get_possible_values(grid, row, col):
    possible = set(range(1, 10))

    for c in range(9):
        possible.discard(grid[row][c])

    for r in range(9):
        possible.discard(grid[r][col])

    box_x = col // 3
    box_y = row // 3
    for r in range(box_y * 3, box_y * 3 + 3):
        for c in range(box_x * 3, box_x * 3 + 3):
            possible.discard(grid[r][c])

    return possible


def mrv(grid):
    best_cell = None
    fewest = 10

    for r in range(9):
        for c in range(9):
            if grid[r][c] == 0:
                options = get_possible_values(grid, r, c)
                if len(options) == 0:
                    return None  # dead end
                if len(options) < fewest:
                    fewest = len(options)
                    best_cell = (r, c)

    return best_cell


def lcv(grid, row, col):
    options = get_possible_values(grid, row, col)
    scores = []

    for value in options:
        eliminated = 0
        grid[row][col] = value

        for r in range(9):
            for c in range(9):
                if grid[r][c] == 0:
                    eliminated += 9 - len(get_possible_values(grid, r, c))

        grid[row][col] = 0
        scores.append((eliminated, value))

    scores.sort()  # least constraining first
    return [v for _, v in scores]
