'''
Game model for Gomoku. Contains the Board class that manages board state, move history,
validation, and win detection logic for a standard 15x15 Gomoku game.
'''
from typing import List, Optional, Tuple
Coord = Tuple[int, int]
Move = Tuple[int, int, int]  # (row, col, player)
class Board:
    """
    Board represents a 15x15 Gomoku board with:
    - 0 for empty
    - 1 for black
    - 2 for white
    It tracks move history and supports undo/redo and win detection.
    """
    def __init__(self, size: int = 15) -> None:
        if size < 5:
            raise ValueError("Board size must be at least 5.")
        self.size = size
        self._grid: List[List[int]] = [[0 for _ in range(size)] for _ in range(size)]
        self._history: List[Move] = []
        self._future: List[Move] = []  # for redo
    def reset(self) -> None:
        """Clears the board and all move history."""
        self._grid = [[0 for _ in range(self.size)] for _ in range(self.size)]
        self._history.clear()
        self._future.clear()
    def in_bounds(self, row: int, col: int) -> bool:
        """Returns True if the given (row, col) is within the board."""
        return 0 <= row < self.size and 0 <= col < self.size
    def get_cell(self, row: int, col: int) -> int:
        """Returns the value at cell: 0 empty, 1 black, 2 white."""
        if not self.in_bounds(row, col):
            raise IndexError("Cell out of bounds.")
        return self._grid[row][col]
    def place_stone(self, row: int, col: int, player: int) -> bool:
        """
        Attempts to place a stone for 'player' at (row, col).
        Returns True if successful, False if the cell is occupied or out of bounds.
        Clears the redo stack when a new move is placed.
        """
        if player not in (1, 2):
            raise ValueError("Player must be 1 (black) or 2 (white).")
        if not self.in_bounds(row, col):
            return False
        if self._grid[row][col] != 0:
            return False
        self._grid[row][col] = player
        self._history.append((row, col, player))
        self._future.clear()
        return True
    def undo(self) -> Optional[Move]:
        """
        Undo the last move and return it. Returns None if history is empty.
        The undone move is pushed onto the redo stack.
        """
        if not self._history:
            return None
        row, col, player = self._history.pop()
        self._grid[row][col] = 0
        self._future.append((row, col, player))
        return (row, col, player)
    def redo(self) -> Optional[Move]:
        """
        Redo the most recently undone move and return it. Returns None if no moves to redo.
        The redone move is appended to the history.
        """
        if not self._future:
            return None
        row, col, player = self._future.pop()
        # Safe because we only redo previously valid moves
        self._grid[row][col] = player
        self._history.append((row, col, player))
        return (row, col, player)
    def is_full(self) -> bool:
        """Returns True if the board is full."""
        for r in range(self.size):
            for c in range(self.size):
                if self._grid[r][c] == 0:
                    return False
        return True
    def last_move(self) -> Optional[Move]:
        """Returns the most recent move or None if no moves have been made."""
        return self._history[-1] if self._history else None
    def _gather_in_direction(
        self, row: int, col: int, dr: int, dc: int, player: int
    ) -> List[Coord]:
        """
        Gather contiguous stones for 'player' starting at (row+dr, col+dc) in the given direction.
        Stops when out of bounds or encountering a different stone.
        Returns the list of coordinates (excluding the starting (row, col)).
        """
        coords: List[Coord] = []
        r, c = row + dr, col + dc
        while self.in_bounds(r, c) and self._grid[r][c] == player:
            coords.append((r, c))
            r += dr
            c += dc
        return coords
    def check_win_from(self, row: int, col: int) -> Tuple[int, Optional[List[Coord]]]:
        """
        Checks if the move at (row, col) wins the game.
        Returns (winner, coords) where winner is 0 (no win), 1 (black), or 2 (white).
        coords is a list of the 5 winning coordinates if a win is found, else None.
        """
        if not self.in_bounds(row, col):
            return 0, None
        player = self._grid[row][col]
        if player not in (1, 2):
            return 0, None
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
        for dr, dc in directions:
            pos = self._gather_in_direction(row, col, dr, dc, player)
            neg = self._gather_in_direction(row, col, -dr, -dc, player)
            line = list(reversed(neg)) + [(row, col)] + pos
            if len(line) >= 5:
                # Choose a contiguous segment of exactly five that includes (row, col)
                origin_index = len(neg)
                start = max(0, min(origin_index, len(line) - 5))
                # Ensure origin is within the 5-length window
                if origin_index - start > 4:
                    start = origin_index - 4
                if start + 5 > len(line):
                    start = len(line) - 5
                winning_coords = line[start: start + 5]
                return player, winning_coords
        return 0, None