'''
Tkinter-based GUI for Reversi (Othello).
Renders the board, handles user interactions, highlights valid moves, displays scores and current player, and manages game flow.
'''
import tkinter as tk
from tkinter import messagebox
from typing import Tuple, Optional
from game import ReversiGame
class ReversiGUI:
    """Tkinter GUI wrapper for the ReversiGame."""
    BOARD_SIZE = 8
    CELL_SIZE = 80  # pixels
    BOARD_PIXEL_SIZE = BOARD_SIZE * CELL_SIZE
    BOARD_BG = "#1f8b4c"  # green felt
    GRID_COLOR = "#0e5b31"
    HINT_COLOR_BLACK = "#444444"
    HINT_COLOR_WHITE = "#dddddd"
    LAST_MOVE_OUTLINE = "#ffcc00"
    def __init__(self, root: tk.Tk) -> None:
        """Create and lay out the GUI."""
        self.root = root
        self.game = ReversiGame()
        # Frame setup
        self.top_frame = tk.Frame(root)
        self.top_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=8)
        self.canvas = tk.Canvas(
            root,
            width=self.BOARD_PIXEL_SIZE,
            height=self.BOARD_PIXEL_SIZE,
            bg=self.BOARD_BG,
            highlightthickness=0,
        )
        self.canvas.pack(side=tk.LEFT, padx=10, pady=10)
        self.side_frame = tk.Frame(root)
        self.side_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        # Status labels
        self.current_player_var = tk.StringVar()
        self.score_var = tk.StringVar()
        self.info_var = tk.StringVar()
        tk.Label(self.top_frame, text="Reversi (Othello)", font=("Arial", 16, "bold")).pack(side=tk.LEFT)
        tk.Label(self.top_frame, textvariable=self.current_player_var, font=("Arial", 12), padx=15).pack(side=tk.LEFT)
        tk.Label(self.top_frame, textvariable=self.score_var, font=("Arial", 12), padx=15).pack(side=tk.LEFT)
        tk.Label(self.top_frame, textvariable=self.info_var, font=("Arial", 11), fg="#333333").pack(side=tk.RIGHT)
        # Buttons
        self.new_game_btn = tk.Button(self.side_frame, text="New Game", width=18, command=self.new_game)
        self.undo_btn = tk.Button(self.side_frame, text="Undo Move", width=18, command=self.undo_move)
        self.quit_btn = tk.Button(self.side_frame, text="Quit", width=18, command=self.root.destroy)
        self.new_game_btn.pack(pady=(0, 8))
        self.undo_btn.pack(pady=8)
        self.quit_btn.pack(pady=8)
        # Hints toggle (always on for clarity)
        self.show_hints = True
        # Bind events
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.root.bind("<n>", lambda e: self.new_game())
        self.root.bind("<u>", lambda e: self.undo_move())
        # Initial draw
        self.update_all()
    def new_game(self) -> None:
        """Reset the game and refresh the UI."""
        self.game.reset()
        self.update_all()
        self.info_var.set("New game started. Black moves first.")
    def undo_move(self) -> None:
        """Undo the last move if possible."""
        if self.game.can_undo():
            self.game.undo()
            self.update_all()
            self.info_var.set("Last move undone.")
        else:
            self.info_var.set("Nothing to undo.")
    def on_canvas_click(self, event) -> None:
        """Handle a click on the board to place a disc if the move is valid."""
        if self.game.current_player is None:
            # Game over
            return
        r = event.y // self.CELL_SIZE
        c = event.x // self.CELL_SIZE
        if not (0 <= r < self.BOARD_SIZE and 0 <= c < self.BOARD_SIZE):
            return
        result = self.game.apply_move(r, c)
        if not result["moved"]:
            # Invalid move
            self.info_var.set("Invalid move. Choose a highlighted cell.")
            self.root.bell()
            return
        # Update UI after a valid move
        self.update_all()
        if result["pass_occurred"]:
            # Opponent had to pass
            passed_player = self.game.opponent(result["current_player"]) if result["current_player"] is not None else None
            self.show_pass_message(passed_player)
        if result["game_over"] or self.game.is_game_over():
            self.show_game_over()
    def update_all(self) -> None:
        """Redraw the board and update status labels."""
        self.canvas.delete("all")
        self.draw_board()
        # Update status
        score = self.game.get_score()
        self.score_var.set(f"Score — Black: {score['black']}  White: {score['white']}")
        if self.game.current_player == ReversiGame.BLACK:
            self.current_player_var.set("Current: Black")
        elif self.game.current_player == ReversiGame.WHITE:
            self.current_player_var.set("Current: White")
        else:
            self.current_player_var.set("Game Over")
        # Info about availability of moves
        if self.game.current_player is not None:
            moves = self.game.get_valid_moves()
            if len(moves) == 0:
                self.info_var.set("No valid moves. Turn will be passed.")
            else:
                self.info_var.set(f"{len(moves)} valid move(s) available.")
        else:
            self.info_var.set("")
    def draw_board(self) -> None:
        """Draw the grid, discs, valid-move hints, and last move marker."""
        # Background and grid
        self.canvas.create_rectangle(0, 0, self.BOARD_PIXEL_SIZE, self.BOARD_PIXEL_SIZE, fill=self.BOARD_BG, outline="")
        for i in range(self.BOARD_SIZE + 1):
            x = i * self.CELL_SIZE
            y = i * self.CELL_SIZE
            self.canvas.create_line(x, 0, x, self.BOARD_PIXEL_SIZE, fill=self.GRID_COLOR, width=2)
            self.canvas.create_line(0, y, self.BOARD_PIXEL_SIZE, y, fill=self.GRID_COLOR, width=2)
        # Draw discs
        for r in range(self.BOARD_SIZE):
            for c in range(self.BOARD_SIZE):
                cell = self.game.board[r][c]
                if cell == ReversiGame.EMPTY:
                    continue
                x0, y0, x1, y1 = self.board_to_canvas_coords(r, c)
                margin = 6
                fill = "#000000" if cell == ReversiGame.BLACK else "#ffffff"
                outline = "#222222" if cell == ReversiGame.BLACK else "#e0e0e0"
                self.canvas.create_oval(
                    x0 + margin, y0 + margin, x1 - margin, y1 - margin,
                    fill=fill, outline=outline, width=2
                )
        # Last move highlight
        if self.game.last_move is not None:
            r, c = self.game.last_move
            x0, y0, x1, y1 = self.board_to_canvas_coords(r, c)
            self.canvas.create_rectangle(
                x0 + 2, y0 + 2, x1 - 2, y1 - 2,
                outline=self.LAST_MOVE_OUTLINE, width=3
            )
        # Valid move hints
        if self.show_hints and self.game.current_player is not None:
            moves = self.game.get_valid_moves()
            for r, c in moves:
                x0, y0, x1, y1 = self.board_to_canvas_coords(r, c)
                cx = (x0 + x1) / 2
                cy = (y0 + y1) / 2
                radius = self.CELL_SIZE * 0.18
                color = self.HINT_COLOR_BLACK if self.game.current_player == ReversiGame.BLACK else self.HINT_COLOR_WHITE
                self.canvas.create_oval(
                    cx - radius, cy - radius, cx + radius, cy + radius,
                    fill=color, outline=""
                )
    def board_to_canvas_coords(self, r: int, c: int) -> Tuple[int, int, int, int]:
        """Convert board cell (r, c) to canvas rectangle coordinates (x0, y0, x1, y1)."""
        x0 = c * self.CELL_SIZE
        y0 = r * self.CELL_SIZE
        x1 = x0 + self.CELL_SIZE
        y1 = y0 + self.CELL_SIZE
        return x0, y0, x1, y1
    def show_pass_message(self, passed_player: Optional[int]) -> None:
        """Display a message indicating that a player had to pass."""
        if passed_player is None:
            return
        name = "Black" if passed_player == ReversiGame.BLACK else "White"
        messagebox.showinfo("Pass", f"{name} has no valid moves and must pass.")
    def show_game_over(self) -> None:
        """Display the game-over dialog with the final result."""
        score = self.game.get_score()
        winner = self.game.get_winner()
        if winner == ReversiGame.BLACK:
            msg = "Black wins!"
        elif winner == ReversiGame.WHITE:
            msg = "White wins!"
        else:
            msg = "It's a tie!"
        messagebox.showinfo(
            "Game Over",
            f"Final Score:\nBlack: {score['black']}   White: {score['white']}\n\n{msg}"
        )