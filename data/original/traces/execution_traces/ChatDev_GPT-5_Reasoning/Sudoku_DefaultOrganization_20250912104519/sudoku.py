'''
Sudoku logic module: board representation, solving, and puzzle generation.
'''
import random
import time
from typing import List, Optional, Tuple
Grid = List[List[int]]
class SudokuBoard:
    """
    Represents a 9x9 Sudoku board and provides solving and generation utilities.
    0 denotes empty cells.
    """
    def __init__(self, grid: Optional[Grid] = None):
        if grid is None:
            self.grid = [[0 for _ in range(9)] for _ in range(9)]
        else:
            # Defensive copy and validation
            if not isinstance(grid, list) or len(grid) != 9 or any(
                not isinstance(row, list) or len(row) != 9 for row in grid
            ):
                raise ValueError("Grid must be a 9x9 list of lists.")
            self.grid = [[int(x) for x in row] for row in grid]
    def copy(self) -> "SudokuBoard":
        """Return a deep copy of the board."""
        return SudokuBoard([row[:] for row in self.grid])
    def to_list(self) -> Grid:
        """Return a list-of-lists representation of the board."""
        return [row[:] for row in self.grid]
    @staticmethod
    def _in_box(r: int, c: int, br: int, bc: int) -> bool:
        """Check if (r,c) is inside the 3x3 box starting at (br,bc)."""
        return br <= r < br + 3 and bc <= c < bc + 3
    def is_valid(self, num: int, row: int, col: int, grid: Optional[Grid] = None) -> bool:
        """
        Check if placing 'num' at (row, col) satisfies Sudoku rules.
        If grid is None, use self.grid.
        """
        if num == 0:
            return True
        if num < 1 or num > 9:
            return False
        g = self.grid if grid is None else grid
        # Check row and column
        for i in range(9):
            if g[row][i] == num and i != col:
                return False
            if g[i][col] == num and i != row:
                return False
        # Check 3x3 subgrid
        br = (row // 3) * 3
        bc = (col // 3) * 3
        for r in range(br, br + 3):
            for c in range(bc, bc + 3):
                if (r != row or c != col) and g[r][c] == num:
                    return False
        return True
    def set_value(self, row: int, col: int, num: int) -> None:
        """Set a value at (row, col)."""
        self.grid[row][col] = num
    def clear_value(self, row: int, col: int) -> None:
        """Clear cell at (row, col) to 0."""
        self.grid[row][col] = 0
    def is_complete(self, grid: Optional[Grid] = None) -> bool:
        """Return True if there are no zeros on the board."""
        g = self.grid if grid is None else grid
        return all(all(val != 0 for val in row) for row in g)
    def is_solved(self, solution: Grid) -> bool:
        """
        Check if current board equals the provided solution.
        """
        return self.grid == solution
    def find_empty(self, grid: Optional[Grid] = None) -> Optional[Tuple[int, int]]:
        """Find the next empty cell. Return (row, col) or None if none."""
        g = self.grid if grid is None else grid
        for r in range(9):
            for c in range(9):
                if g[r][c] == 0:
                    return r, c
        return None
    def solve(self, grid: Optional[Grid] = None) -> bool:
        """
        Solve the Sudoku using backtracking. If grid is provided, solve that grid in-place.
        Returns True if solved, False otherwise.
        """
        g = self.grid if grid is None else grid
        empty = self.find_empty(g)
        if not empty:
            return True
        row, col = empty
        nums = list(range(1, 10))
        for n in nums:
            if self.is_valid(n, row, col, g):
                g[row][col] = n
                if self.solve(g):
                    return True
                g[row][col] = 0
        return False
    def count_solutions(self, grid: Optional[Grid] = None, max_solutions: int = 2) -> int:
        """
        Count number of solutions up to max_solutions. Uses backtracking with early cutoff.
        """
        g = self.grid if grid is None else grid
        count = 0
        def backtrack() -> None:
            nonlocal count, g
            if count >= max_solutions:
                return
            empt = self.find_empty(g)
            if not empt:
                count += 1
                return
            r, c = empt
            for n in range(1, 10):
                if self.is_valid(n, r, c, g):
                    g[r][c] = n
                    backtrack()
                    if count >= max_solutions:
                        g[r][c] = 0
                        return
                    g[r][c] = 0
        backtrack()
        return count
    def generate_full(self) -> Grid:
        """
        Generate a complete valid Sudoku solution using randomized backtracking.
        Returns the solved grid.
        """
        g = [[0] * 9 for _ in range(9)]
        def fill_cell() -> bool:
            empt = self.find_empty(g)
            if not empt:
                return True
            r, c = empt
            nums = list(range(1, 10))
            random.shuffle(nums)
            for n in nums:
                if self.is_valid(n, r, c, g):
                    g[r][c] = n
                    if fill_cell():
                        return True
                    g[r][c] = 0
            return False
        fill_cell()
        self.grid = g
        return self.to_list()
    def generate_puzzle(self, difficulty: str = "medium", max_time: float = 3.0) -> Tuple[Grid, Grid]:
        """
        Generate a Sudoku puzzle with a unique solution and return (puzzle, solution).
        difficulty: 'easy' | 'medium' | 'hard' affects number of removals.
        max_time: time budget in seconds for uniqueness enforcement; fallback if exceeded.
        Approach:
        - Generate a full solution.
        - Attempt to remove cells randomly while preserving unique solution.
        """
        # Generate a complete solution first
        solution = self.generate_full()
        # Determine removal target by difficulty
        difficulty = (difficulty or "medium").lower()
        if difficulty == "easy":
            target_remove = random.randint(30, 36)
        elif difficulty == "hard":
            target_remove = random.randint(50, 58)
        else:
            target_remove = random.randint(40, 48)
        puzzle = [row[:] for row in solution]
        # Create list of all cell indices and shuffle
        cells = [(r, c) for r in range(9) for c in range(9)]
        random.shuffle(cells)
        removed = 0
        start = time.time()
        # Try removing values while ensuring uniqueness
        for (r, c) in cells:
            if time.time() - start > max_time:
                break  # time budget exceeded; fallback with current puzzle
            if puzzle[r][c] == 0:
                continue
            saved = puzzle[r][c]
            puzzle[r][c] = 0
            # Check uniqueness
            temp = [row[:] for row in puzzle]
            sol_count = self.count_solutions(temp, max_solutions=2)
            if sol_count != 1:
                # not unique, revert
                puzzle[r][c] = saved
            else:
                removed += 1
                if removed >= target_remove:
                    break
        # Fallback: ensure at least some removals; if none removed, use a predefined puzzle
        if removed < 20:
            sample_puzzle, sample_solution = get_sample_puzzle()
            return sample_puzzle, sample_solution
        return puzzle, solution
def get_sample_puzzle() -> Tuple[Grid, Grid]:
    """
    Provide a predefined puzzle/solution pair as a reliable fallback.
    """
    # A known Sudoku puzzle with unique solution
    puzzle = [
        [0, 0, 0, 2, 6, 0, 7, 0, 1],
        [6, 8, 0, 0, 7, 0, 0, 9, 0],
        [1, 9, 0, 0, 0, 4, 5, 0, 0],
        [8, 2, 0, 1, 0, 0, 0, 4, 0],
        [0, 0, 4, 6, 0, 2, 9, 0, 0],
        [0, 5, 0, 0, 0, 3, 0, 2, 8],
        [0, 0, 9, 3, 0, 0, 0, 7, 4],
        [0, 4, 0, 0, 5, 0, 0, 3, 6],
        [7, 0, 3, 0, 1, 8, 0, 0, 0],
    ]
    # Its solution
    solution = [
        [4, 3, 5, 2, 6, 9, 7, 8, 1],
        [6, 8, 2, 5, 7, 1, 4, 9, 3],
        [1, 9, 7, 8, 3, 4, 5, 6, 2],
        [8, 2, 6, 1, 9, 5, 3, 4, 7],
        [3, 7, 4, 6, 8, 2, 9, 1, 5],
        [9, 5, 1, 7, 4, 3, 6, 2, 8],
        [5, 1, 9, 3, 2, 6, 8, 7, 4],
        [2, 4, 8, 9, 5, 7, 1, 3, 6],
        [7, 6, 3, 4, 1, 8, 2, 5, 9],
    ]
    return puzzle, solution
def generate_puzzle(difficulty: str = "medium") -> Tuple[Grid, Grid]:
    """
    Convenience function to create a fresh Sudoku puzzle and its solution.
    """
    board = SudokuBoard()
    return board.generate_puzzle(difficulty=difficulty)