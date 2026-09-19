'''
Connect Four game logic module.
Defines the ConnectFourGame class which encapsulates the board, rules,
turn management, win/draw detection, and move validation.
'''
from typing import List, Optional, Tuple
class ConnectFourGame:
    """Encapsulates the game state and rules for Connect Four."""
    def __init__(self, rows: int = 6, cols: int = 7) -> None:
        """Initialize a new game with the given dimensions."""
        if rows < 4 or cols < 4:
            raise ValueError("Connect Four requires at least 4 rows and 4 columns.")
        self.rows = rows
        self.cols = cols
        self.board: List[List[int]] = []
        self.current_player: int = 1
        self.winner: Optional[int] = None
        self.game_over: bool = False
        self.move_count: int = 0
        self.last_move: Optional[Tuple[int, int]] = None
        self.reset()
    def reset(self) -> None:
        """Reset the game to its initial state."""
        self.board = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        self.current_player = 1
        self.winner = None
        self.game_over = False
        self.move_count = 0
        self.last_move = None
    def get_board(self) -> Tuple[Tuple[int, ...], ...]:
        """Return an immutable snapshot of the current board."""
        return tuple(tuple(row) for row in self.board)
    def get_current_player(self) -> int:
        """Return the current player's numeric ID (1 or 2)."""
        return self.current_player
    def get_winner(self) -> Optional[int]:
        """Return the winner's ID, or None if no winner yet."""
        return self.winner
    def is_valid_move(self, col: int) -> bool:
        """
        Return True if a disc can be dropped in the given column.
        A move is valid if 0 <= col < cols and the column is not full.
        """
        if self.game_over:
            return False
        if not (0 <= col < self.cols):
            return False
        # If top cell is empty, column has space
        return self.board[0][col] == 0
    def _find_available_row(self, col: int) -> int:
        """Return the lowest available row index in the specified column."""
        for r in range(self.rows - 1, -1, -1):
            if self.board[r][col] == 0:
                return r
        raise ValueError("Column is full.")
    def drop_disc(self, col: int) -> int:
        """
        Drop a disc for the current player in the given column.
        Returns the row index where the disc lands.
        Raises ValueError for invalid moves or if the game is over.
        """
        if self.game_over:
            raise ValueError("The game is already over.")
        if not (0 <= col < self.cols):
            raise ValueError(f"Column must be between 0 and {self.cols - 1}.")
        if not self.is_valid_move(col):
            raise ValueError("Invalid move: column is full or out of range.")
        row = self._find_available_row(col)
        self.board[row][col] = self.current_player
        self.last_move = (row, col)
        self.move_count += 1
        if self.check_win(row, col):
            self.winner = self.current_player
            self.game_over = True
        elif self.check_draw():
            self.game_over = True
        else:
            self.switch_player()
        return row
    def check_draw(self) -> bool:
        """Return True if the board is full and there is no winner."""
        return self.move_count >= self.rows * self.cols and self.winner is None
    def switch_player(self) -> None:
        """Switch to the other player."""
        self.current_player = 2 if self.current_player == 1 else 1
    def count_in_direction(
        self, row: int, col: int, dr: int, dc: int, player: int
    ) -> int:
        """
        Count consecutive discs for 'player' including (row, col),
        extending in the (dr, dc) and (-dr, -dc) directions.
        """
        count = 1
        # Forward direction
        r, c = row + dr, col + dc
        while 0 <= r < self.rows and 0 <= c < self.cols and self.board[r][c] == player:
            count += 1
            r += dr
            c += dc
        # Backward direction
        r, c = row - dr, col - dc
        while 0 <= r < self.rows and 0 <= c < self.cols and self.board[r][c] == player:
            count += 1
            r -= dr
            c -= dc
        return count
    def check_win(self, row: int, col: int) -> bool:
        """Return True if the move at (row, col) created a four-in-a-row."""
        player = self.board[row][col]
        if player == 0:
            return False
        directions = [
            (0, 1),   # Horizontal
            (1, 0),   # Vertical
            (1, 1),   # Diagonal down-right
            (-1, 1),  # Diagonal up-right
        ]
        for dr, dc in directions:
            if self.count_in_direction(row, col, dr, dc, player) >= 4:
                return True
        return False