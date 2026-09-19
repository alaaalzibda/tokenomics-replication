'''
Game logic for Reversi (Othello).
Contains the ReversiGame class that manages the board, moves, flipping, turns, scoring, and undo.
'''
from typing import List, Tuple, Dict, Optional
class ReversiGame:
    """Encapsulates all rules and state for a standard 8x8 Reversi game."""
    EMPTY = 0
    BLACK = 1
    WHITE = 2
    DIRECTIONS: List[Tuple[int, int]] = [
        (-1, -1), (-1, 0), (-1, 1),
        (0, -1),           (0, 1),
        (1, -1),  (1, 0),  (1, 1),
    ]
    def __init__(self) -> None:
        """Initialize a new game."""
        self.size: int = 8
        self.board: List[List[int]] = [[self.EMPTY for _ in range(self.size)] for _ in range(self.size)]
        self.current_player: int = self.BLACK  # Black moves first
        self.last_move: Optional[Tuple[int, int]] = None
        # History for undo: list of tuples (board_copy, current_player, last_move)
        self._history: List[Tuple[List[List[int]], int, Optional[Tuple[int, int]]]] = []
        self.reset()
    def reset(self) -> None:
        """Reset the game to the initial starting position."""
        self.board = [[self.EMPTY for _ in range(self.size)] for _ in range(self.size)]
        self.initialize_board()
        self.current_player = self.BLACK
        self.last_move = None
        self._history.clear()
    def initialize_board(self) -> None:
        """Place the four initial discs in the center of the board."""
        mid = self.size // 2
        # Standard initial setup:
        # (3,3)=WHITE, (3,4)=BLACK, (4,3)=BLACK, (4,4)=WHITE
        self.board[mid - 1][mid - 1] = self.WHITE
        self.board[mid - 1][mid] = self.BLACK
        self.board[mid][mid - 1] = self.BLACK
        self.board[mid][mid] = self.WHITE
    def snapshot(self) -> None:
        """Save a snapshot of the current state for undo functionality."""
        board_copy = [row[:] for row in self.board]
        self._history.append((board_copy, self.current_player, self.last_move))
    def can_undo(self) -> bool:
        """Return True if there is at least one move to undo."""
        return len(self._history) > 0
    def undo(self) -> bool:
        """Undo the last move; return True if successful, False if history empty."""
        if not self._history:
            return False
        board_copy, player, last_move = self._history.pop()
        self.board = [row[:] for row in board_copy]
        self.current_player = player
        self.last_move = last_move
        return True
    def in_bounds(self, r: int, c: int) -> bool:
        """Check if (r, c) are valid board coordinates."""
        return 0 <= r < self.size and 0 <= c < self.size
    def opponent(self, player: int) -> int:
        """Return opponent color of a given player."""
        return self.BLACK if player == self.WHITE else self.WHITE
    def _discs_to_flip(self, r: int, c: int, player: int) -> List[Tuple[int, int]]:
        """
        Given a candidate placement (r, c) for 'player', return a list of discs that would be flipped.
        Returns an empty list if move is invalid (i.e., flips no discs).
        """
        if not self.in_bounds(r, c) or self.board[r][c] != self.EMPTY:
            return []
        flips: List[Tuple[int, int]] = []
        opp = self.opponent(player)
        for dr, dc in self.DIRECTIONS:
            path: List[Tuple[int, int]] = []
            rr, cc = r + dr, c + dc
            # First step in a direction must be opponent's disc
            if not self.in_bounds(rr, cc) or self.board[rr][cc] != opp:
                continue
            # Move along while encountering opponent discs
            while self.in_bounds(rr, cc) and self.board[rr][cc] == opp:
                path.append((rr, cc))
                rr += dr
                cc += dc
            # If we ended on a player disc, we can flip the path
            if self.in_bounds(rr, cc) and self.board[rr][cc] == player and path:
                flips.extend(path)
            # Else, no capture in this direction
        return flips
    def get_valid_moves(self, player: Optional[int] = None) -> List[Tuple[int, int]]:
        """Compute and return all valid moves for the given player (or current player if None)."""
        if player is None:
            player = self.current_player
        valid: List[Tuple[int, int]] = []
        for r in range(self.size):
            for c in range(self.size):
                if self.board[r][c] == self.EMPTY:
                    to_flip = self._discs_to_flip(r, c, player)
                    if to_flip:
                        valid.append((r, c))
        return valid
    def is_valid_move(self, r: int, c: int, player: Optional[int] = None) -> bool:
        """Return True if placing at (r, c) is a valid move for player."""
        if player is None:
            player = self.current_player
        return len(self._discs_to_flip(r, c, player)) > 0
    def apply_move(self, r: int, c: int) -> Dict[str, object]:
        """
        Apply a move for the current player at (r, c).
        Returns a dict with keys:
          - moved (bool)
          - flipped (int)
          - placed (tuple)  # (r, c) if moved else None
          - current_player (int or None)  # next player after processing pass/game over
          - pass_occurred (bool)
          - game_over (bool)
          - scores (dict)  # {'black': int, 'white': int}
        """
        result = {
            "moved": False,
            "flipped": 0,
            "placed": None,
            "current_player": self.current_player,
            "pass_occurred": False,
            "game_over": False,
            "scores": self.get_score(),
        }
        if not self.is_valid_move(r, c, self.current_player):
            return result  # invalid move, no change
        # Save history for undo
        self.snapshot()
        player = self.current_player
        flips = self._discs_to_flip(r, c, player)
        # Place disc
        self.board[r][c] = player
        # Flip discs
        for rr, cc in flips:
            self.board[rr][cc] = player
        self.last_move = (r, c)
        result["moved"] = True
        result["flipped"] = len(flips)
        result["placed"] = (r, c)
        # Determine next turn, handle passes and game over
        next_player = self.opponent(player)
        if self.has_valid_move(next_player):
            self.current_player = next_player
        else:
            # Opponent cannot move
            if self.has_valid_move(player):
                # Current player moves again (pass occurs)
                self.current_player = player
                result["pass_occurred"] = True
            else:
                # Neither can move: game over
                self.current_player = None  # No current player when game ends
                result["game_over"] = True
        result["current_player"] = self.current_player
        result["scores"] = self.get_score()
        return result
    def has_valid_move(self, player: int) -> bool:
        """Return True if the player has at least one valid move."""
        return any(
            self.is_valid_move(r, c, player)
            for r in range(self.size)
            for c in range(self.size)
            if self.board[r][c] == self.EMPTY
        )
    def is_game_over(self) -> bool:
        """Game is over if neither player has a valid move or the board is full."""
        # Quick board full check
        if all(cell != self.EMPTY for row in self.board for cell in row):
            return True
        # Check valid moves for both
        return not self.has_valid_move(self.BLACK) and not self.has_valid_move(self.WHITE)
    def get_score(self) -> Dict[str, int]:
        """Return the current score as a dict with 'black' and 'white' counts."""
        black = sum(1 for row in self.board for cell in row if cell == self.BLACK)
        white = sum(1 for row in self.board for cell in row if cell == self.WHITE)
        return {"black": black, "white": white}
    def get_winner(self) -> int:
        """
        Return the winner: ReversiGame.BLACK, ReversiGame.WHITE, or 0 for tie.
        If game not over, still computes based on current counts.
        """
        score = self.get_score()
        if score["black"] > score["white"]:
            return self.BLACK
        if score["white"] > score["black"]:
            return self.WHITE
        return 0