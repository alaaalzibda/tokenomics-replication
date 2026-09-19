'''
Game logic for 2048, including move mechanics, merging rules, scoring, and state serialization.
'''
import random
from typing import List, Tuple, Dict, Optional
class Game2048:
    """
    Core 2048 game mechanics on an NxN board (default 4x4).
    """
    def __init__(self, size: int = 4, board: Optional[List[List[int]]] = None,
                 score: int = 0, max_tile: int = 0):
        self.size = size
        if board is None:
            self.board = [[0 for _ in range(self.size)] for _ in range(self.size)]
            self.score = 0
            self.max_tile = 0
            # Spawn two tiles at start
            self.add_random_tile()
            self.add_random_tile()
        else:
            # Initialize from existing state
            self.board = [row[:] for row in board]
            self.score = score
            self.max_tile = max(max_tile, self.get_max_tile())
    def reset(self) -> None:
        """Reset the game to initial state with two random tiles."""
        self.board = [[0 for _ in range(self.size)] for _ in range(self.size)]
        self.score = 0
        self.max_tile = 0
        self.add_random_tile()
        self.add_random_tile()
    def add_random_tile(self) -> bool:
        """
        Add a new tile (2 with 90% probability, 4 with 10%) at a random empty position.
        Returns True if a tile was added, False if no empty cell exists.
        """
        empty = [(r, c) for r in range(self.size) for c in range(self.size) if self.board[r][c] == 0]
        if not empty:
            return False
        r, c = random.choice(empty)
        value = 4 if random.random() < 0.1 else 2
        self.board[r][c] = value
        if value > self.max_tile:
            self.max_tile = value
        return True
    def move(self, direction: str) -> Tuple[bool, int]:
        """
        Execute a move in the given direction: 'up', 'down', 'left', 'right'.
        Returns (changed, gained_score).
        """
        changed = False
        gained_total = 0
        if direction not in ('up', 'down', 'left', 'right'):
            return False, 0
        def apply_to_line(line: List[int]) -> Tuple[List[int], int]:
            new_line, gained = self.move_line(line)
            return new_line, gained
        if direction in ('left', 'right'):
            for r in range(self.size):
                row = self.board[r][:]
                if direction == 'right':
                    row = row[::-1]
                new_row, gained = apply_to_line(row)
                if direction == 'right':
                    new_row = new_row[::-1]
                if new_row != self.board[r]:
                    changed = True
                    self.board[r] = new_row
                if gained:
                    self.score += gained
                    if max(new_row) > self.max_tile:
                        self.max_tile = max(self.max_tile, max(new_row))
                    gained_total += gained
        else:
            # up or down works on columns
            for c in range(self.size):
                col = [self.board[r][c] for r in range(self.size)]
                if direction == 'down':
                    col = col[::-1]
                new_col, gained = apply_to_line(col)
                if direction == 'down':
                    new_col = new_col[::-1]
                # apply back to board
                for r in range(self.size):
                    if self.board[r][c] != new_col[r]:
                        changed = True
                        self.board[r][c] = new_col[r]
                if gained:
                    self.score += gained
                    if max(new_col) > self.max_tile:
                        self.max_tile = max(self.max_tile, max(new_col))
                    gained_total += gained
        return changed, gained_total
    def move_line(self, line: List[int]) -> Tuple[List[int], int]:
        """
        Given a line (row/column) oriented towards the left, compress and merge.
        Returns (new_line, gained_score).
        Example: [2, 0, 2, 4] -> [4, 4, 0, 0], gained=4.
        """
        size = self.size
        tiles = [x for x in line if x != 0]  # compress
        gained = 0
        merged: List[int] = []
        skip = False
        for i in range(len(tiles)):
            if skip:
                skip = False
                continue
            if i + 1 < len(tiles) and tiles[i] == tiles[i + 1]:
                new_val = tiles[i] * 2
                merged.append(new_val)
                gained += new_val
                skip = True  # skip the next tile (it has been merged)
            else:
                merged.append(tiles[i])
        # pad with zeros
        merged += [0] * (size - len(merged))
        return merged, gained
    def can_move(self) -> bool:
        """
        Check if any move is possible (empty cells or adjacent equal tiles).
        """
        # If any empty cell, move is possible
        for r in range(self.size):
            for c in range(self.size):
                if self.board[r][c] == 0:
                    return True
        # Check horizontal merges
        for r in range(self.size):
            for c in range(self.size - 1):
                if self.board[r][c] == self.board[r][c + 1]:
                    return True
        # Check vertical merges
        for c in range(self.size):
            for r in range(self.size - 1):
                if self.board[r][c] == self.board[r + 1][c]:
                    return True
        return False
    def get_max_tile(self) -> int:
        """Return the maximum tile on the board."""
        return max(max(row) for row in self.board) if self.board else 0
    def to_state(self) -> Dict:
        """Serialize the game state."""
        return {
            'size': self.size,
            'board': [row[:] for row in self.board],
            'score': self.score,
            'max_tile': self.max_tile,
        }
    @staticmethod
    def from_state(state: Dict) -> 'Game2048':
        """Deserialize a game from a saved state dict."""
        size = state.get('size', 4)
        board = state.get('board', [[0] * size for _ in range(size)])
        score = state.get('score', 0)
        max_tile = state.get('max_tile', 0)
        return Game2048(size=size, board=board, score=score, max_tile=max_tile)