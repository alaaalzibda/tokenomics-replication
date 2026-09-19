'''
Controller for the Gomoku game. It coordinates between the model (Board) and the view (GUI),
handles user interactions (clicks, undo/redo, new game), and manages turn order and status.
'''
from typing import Optional, List, Tuple
# Support both package and flat-file imports
try:
    from .model import Board
except ImportError:
    from model import Board
Coord = Tuple[int, int]
class GameController:
    """
    GameController manages the game flow:
    - Tracks current player and game-over state
    - Delegates move placement to the model
    - Detects wins and draws
    - Notifies the view to refresh and present results
    """
    def __init__(self) -> None:
        self.board = Board(size=15)
        self.current_player: int = 1  # 1 = black, 2 = white
        self.game_over: bool = False
        self.winner: int = 0
        self.winning_coords: Optional[List[Coord]] = None
        self._view = None  # attached later
    def attach_view(self, view) -> None:
        """Attach the view so the controller can trigger refreshes and notifications."""
        self._view = view
        # Initial refresh to sync UI
        if self._view:
            self._view.refresh()
    def start_new_game(self) -> None:
        """Reset the game state and notify the view."""
        self.board.reset()
        self.current_player = 1
        self.game_over = False
        self.winner = 0
        self.winning_coords = None
        if self._view:
            self._view.refresh()
    def handle_board_click(self, row: int, col: int) -> None:
        """
        Handle a click on the board at the given logical coordinates.
        Attempts to place a stone for the current player, then checks for a win or draw.
        """
        if self.game_over:
            return
        if not self.board.place_stone(row, col, self.current_player):
            # Invalid move (occupied or out of bounds)
            return
        # Check win from the last move
        winner, coords = self.board.check_win_from(row, col)
        if winner != 0:
            self.game_over = True
            self.winner = winner
            self.winning_coords = coords
            if self._view:
                self._view.refresh()
                self._view.show_winner(winner, coords)
            return
        # Check draw
        if self.board.is_full():
            self.game_over = True
            self.winner = 0
            self.winning_coords = None
            if self._view:
                self._view.refresh()
            return
        # Next player's turn
        self.current_player = 2 if self.current_player == 1 else 1
        if self._view:
            self._view.refresh()
    def undo_move(self) -> None:
        """
        Undo the last move. If successful, change current player accordingly and clear any end state.
        """
        undone = self.board.undo()
        if undone is None:
            return
        # Set the current player to the one who played the undone move
        _, _, player = undone
        self.current_player = player
        # Clear game-over state and winning highlight since the position changed
        self.game_over = False
        self.winner = 0
        self.winning_coords = None
        if self._view:
            self._view.refresh()
    def redo_move(self) -> None:
        """
        Redo the most recently undone move (if any). Recompute win/draw and update state.
        """
        if self.game_over:
            return
        redone = self.board.redo()
        if redone is None:
            return
        row, col, player = redone
        # After redoing a move, it's now the other player's turn
        self.current_player = 2 if player == 1 else 1
        winner, coords = self.board.check_win_from(row, col)
        if winner != 0:
            self.game_over = True
            self.winner = winner
            self.winning_coords = coords
        elif self.board.is_full():
            self.game_over = True
            self.winner = 0
            self.winning_coords = None
        if self._view:
            self._view.refresh()
            if self.game_over and self.winner != 0:
                self._view.show_winner(self.winner, self.winning_coords)
    def get_status_text(self) -> str:
        """
        Return a human-readable status string for the UI.
        """
        if self.game_over:
            if self.winner == 1:
                return "Game Over: Black wins!"
            elif self.winner == 2:
                return "Game Over: White wins!"
            else:
                return "Game Over: Draw."
        else:
            return "Turn: Black" if self.current_player == 1 else "Turn: White"