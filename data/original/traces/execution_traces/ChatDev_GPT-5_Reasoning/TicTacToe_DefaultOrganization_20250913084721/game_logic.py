'''
Core game logic for Tic-Tac-Toe.
This module defines the TicTacToeGame class which encapsulates the board,
turn management, move validation, and win/draw detection.
Enhancements:
- Tracks and alternates the starting player across games for fairness.
'''
from typing import List, Optional, Tuple
from constants import GRID_SIZE, SYMBOL_X, SYMBOL_O
class TicTacToeGame:
    """Game state and logic for a standard 3x3 Tic-Tac-Toe."""
    def __init__(self) -> None:
        self.grid_size: int = GRID_SIZE
        self.symbols = (SYMBOL_X, SYMBOL_O)
        self.board: List[List[str]] = []
        self.current_player: str = SYMBOL_X
        self.move_count: int = 0
        self.winner: Optional[str] = None
        self.winning_line: Optional[List[Tuple[int, int]]] = None
        self.next_starting_player: str = SYMBOL_X  # Alternates after each reset
        self.reset(alternate=False)
    def reset(self, alternate: bool = False) -> None:
        """Reset the game to its initial state.
        Args:
            alternate: If True, alternate who starts compared to the last game.
                       If False, X starts (used for initial game).
        """
        self.board = [["" for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        if alternate:
            self.current_player = self.next_starting_player
        else:
            self.current_player = SYMBOL_X
        # Prepare the next starting player for subsequent resets
        self.next_starting_player = SYMBOL_O if self.current_player == SYMBOL_X else SYMBOL_X
        self.move_count = 0
        self.winner = None
        self.winning_line = None
    def make_move(self, row: int, col: int) -> bool:
        """
        Attempt to place the current player's symbol at (row, col).
        Returns True if the move is successful; False otherwise.
        """
        if self.winner is not None or self.is_draw():
            return False
        if not (0 <= row < self.grid_size and 0 <= col < self.grid_size):
            return False
        if self.board[row][col] != "":
            return False
        self.board[row][col] = self.current_player
        self.move_count += 1
        winner, line = self.check_winner()
        if winner:
            self.winner = winner
            self.winning_line = line
            return True
        if self.is_draw():
            # It's a draw; no need to switch players
            return True
        # Switch turns
        self.current_player = SYMBOL_O if self.current_player == SYMBOL_X else SYMBOL_X
        return True
    def get_cell(self, row: int, col: int) -> str:
        """Get the symbol at a given cell or empty string if unoccupied."""
        if 0 <= row < self.grid_size and 0 <= col < self.grid_size:
            return self.board[row][col]
        return ""
    def available_moves(self) -> List[Tuple[int, int]]:
        """Return a list of available (row, col) moves."""
        moves: List[Tuple[int, int]] = []
        for r in range(self.grid_size):
            for c in range(self.grid_size):
                if self.board[r][c] == "":
                    moves.append((r, c))
        return moves
    def is_draw(self) -> bool:
        """Return True if the game is a draw (board full, no winner)."""
        return self.winner is None and self.move_count >= self.grid_size * self.grid_size
    def check_winner(self) -> Tuple[Optional[str], Optional[List[Tuple[int, int]]]]:
        """
        Check the board for a winner.
        Returns:
            (winner_symbol, winning_line) where winner_symbol is 'X' or 'O' or None,
            and winning_line is a list of (row, col) tuples or None.
        """
        b = self.board
        n = self.grid_size
        # Check rows
        for r in range(n):
            if b[r][0] != "" and all(b[r][c] == b[r][0] for c in range(1, n)):
                return b[r][0], [(r, c) for c in range(n)]
        # Check columns
        for c in range(n):
            if b[0][c] != "" and all(b[r][c] == b[0][c] for r in range(1, n)):
                return b[0][c], [(r, c) for r in range(n)]
        # Check main diagonal
        if b[0][0] != "" and all(b[i][i] == b[0][0] for i in range(1, n)):
            return b[0][0], [(i, i) for i in range(n)]
        # Check anti-diagonal
        if b[0][n - 1] != "" and all(b[i][n - 1 - i] == b[0][n - 1] for i in range(1, n)):
            return b[0][n - 1], [(i, n - 1 - i) for i in range(n)]
        return None, None