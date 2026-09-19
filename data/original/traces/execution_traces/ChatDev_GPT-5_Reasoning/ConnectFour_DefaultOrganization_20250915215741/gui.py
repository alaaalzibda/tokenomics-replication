'''
Tkinter-based GUI for Connect Four.
Provides a visual board, status/turn display, text entry for column selection,
and controls for submitting moves and resetting the game.
Fixes applied:
- Removed global Return key binding to prevent double submission.
- Added early guard in on_submit to preserve end-game status and stop handling.
- Return "break" from on_submit to stop event propagation on Entry's Return.
- Avoid focusing a disabled Entry after the game ends.
- Use dynamic column range (1-{self.game.cols}) across all user messages.
'''
import tkinter as tk
from typing import Optional
from game import ConnectFourGame
class ConnectFourGUI:
    """Graphical user interface for the Connect Four game."""
    def __init__(self, root: tk.Tk, game: ConnectFourGame) -> None:
        self.root = root
        self.game = game
        # Visual layout parameters
        self.cell_size = 80
        self.margin = 20
        self.board_bg = "#1E5AB6"  # Classic board blue
        self.empty_color = "#F2F3F5"
        self.player_colors = {
            1: "#E74C3C",  # Red
            2: "#F1C40F",  # Yellow
        }
        # Derived sizes
        self.canvas_width = self.margin * 2 + self.game.cols * self.cell_size
        self.canvas_height = self.margin * 2 + self.game.rows * self.cell_size
        # State
        self.status_var = tk.StringVar()
        self._build_widgets()
        self.draw_board()
        self.update_status()
    def _build_widgets(self) -> None:
        """Create and lay out GUI widgets."""
        # Status label
        status_frame = tk.Frame(self.root)
        status_frame.pack(padx=10, pady=(10, 5), fill=tk.X)
        status_label = tk.Label(
            status_frame, textvariable=self.status_var, anchor="w", font=("Segoe UI", 11)
        )
        status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        # Canvas for board
        self.canvas = tk.Canvas(
            self.root,
            width=self.canvas_width,
            height=self.canvas_height + 30,  # extra for column numbers
            bg="#ffffff",
            highlightthickness=0,
        )
        self.canvas.pack(padx=10, pady=5)
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        # Controls for typed input
        controls = tk.Frame(self.root)
        controls.pack(padx=10, pady=(5, 10), fill=tk.X)
        tk.Label(
            controls, text=f"Column (1-{self.game.cols}):", font=("Segoe UI", 10)
        ).pack(side=tk.LEFT)
        self.column_var = tk.StringVar()
        self.column_entry = tk.Entry(controls, width=5, textvariable=self.column_var)
        self.column_entry.pack(side=tk.LEFT, padx=(5, 5))
        self.column_entry.bind("<Return>", self.on_submit)
        self.submit_button = tk.Button(
            controls, text="Drop", command=self.on_submit, width=8
        )
        self.submit_button.pack(side=tk.LEFT, padx=(5, 15))
        self.reset_button = tk.Button(
            controls, text="Reset", command=self.reset_game, width=8
        )
        self.reset_button.pack(side=tk.LEFT)
        # Removed global Enter key binding to prevent double handling
        # self.root.bind("<Return>", self.on_submit)
    def focus_column_entry(self) -> None:
        """Give focus to the column entry for immediate typing."""
        self.column_entry.focus_set()
        self.column_entry.selection_range(0, tk.END)
    def update_status(self, message: Optional[str] = None) -> None:
        """Update the status bar with current turn or custom message."""
        if message:
            self.status_var.set(message)
            return
        if self.game.game_over:
            if self.game.get_winner():
                player = self.game.get_winner()
                color = "Red" if player == 1 else "Yellow"
                self.status_var.set(f"Player {player} ({color}) wins! Press Reset to play again.")
            else:
                self.status_var.set("It's a draw! Press Reset to play again.")
        else:
            player = self.game.get_current_player()
            color = "Red" if player == 1 else "Yellow"
            self.status_var.set(
                f"Player {player} ({color}) to move. Enter a column number (1-{self.game.cols})."
            )
    def draw_board(self) -> None:
        """Render the Connect Four board and discs."""
        self.canvas.delete("all")
        # Draw column numbers
        for c in range(self.game.cols):
            x_center = self.margin + c * self.cell_size + self.cell_size / 2
            self.canvas.create_text(
                x_center,
                10,
                text=str(c + 1),
                font=("Segoe UI", 10, "bold"),
                fill="#333333",
            )
        # Board background rectangle
        self.canvas.create_rectangle(
            self.margin,
            self.margin + 20,
            self.canvas_width - self.margin,
            self.canvas_height + 20 - self.margin,
            fill=self.board_bg,
            width=0,
        )
        # Draw cells as "holes" and discs
        padding = self.cell_size * 0.1
        for r in range(self.game.rows):
            for c in range(self.game.cols):
                x0 = self.margin + c * self.cell_size + padding
                y0 = self.margin + 20 + r * self.cell_size + padding
                x1 = self.margin + (c + 1) * self.cell_size - padding
                y1 = self.margin + 20 + (r + 1) * self.cell_size - padding
                val = self.game.board[r][c]
                color = self.empty_color if val == 0 else self.player_colors.get(val, "#000000")
                # Draw the "hole" as a circle by overlaying an oval with the disc color
                self.canvas.create_oval(x0, y0, x1, y1, fill=color, outline="#0D3B8E", width=2)
    def on_submit(self, event=None) -> None:
        """
        Handle 'Drop' button or Enter key to submit the typed column.
        Returns "break" when triggered by an event to stop further propagation.
        """
        # Early guard: preserve final status and avoid handling after game end
        if self.game.game_over:
            self.update_status()  # preserves winner/draw message
            return "break" if event is not None else None
        text = self.column_var.get().strip()
        if not text:
            self.update_status(f"Please type a column number (1-{self.game.cols}).")
        else:
            try:
                col_input = int(text)
            except ValueError:
                self.update_status(f"Invalid input. Enter a number from 1 to {self.game.cols}.")
            else:
                self.attempt_move(col_input - 1)
        # Ensure single handling for Entry's Return
        if event is not None:
            return "break"
    def attempt_move(self, col: int) -> None:
        """Attempt to make a move in the specified column (0-indexed)."""
        if self.game.game_over:
            self.update_status("The game is over. Press Reset to play again.")
            return
        # Validate range explicitly for clear feedback
        if not (0 <= col < self.game.cols):
            self.update_status(f"Column must be between 1 and {self.game.cols}.")
            self.column_entry.selection_range(0, tk.END)
            return
        # Attempt move
        try:
            _ = self.game.drop_disc(col)
        except ValueError as e:
            # Likely column full or game over
            msg = str(e)
            if "full" in msg:
                self.update_status("That column is full. Try a different one.")
            elif "over" in msg:
                self.update_status("The game is over. Press Reset to play again.")
            else:
                self.update_status(msg)
        else:
            # Successful move
            self.draw_board()
            if self.game.game_over:
                self.end_game_feedback()
            else:
                self.update_status()
        finally:
            # Clear and (if enabled) refocus the entry for quick subsequent typing
            if str(self.column_entry["state"]) == "normal":
                self.column_var.set("")
                self.focus_column_entry()
            else:
                self.column_var.set("")
    def on_canvas_click(self, event) -> None:
        """
        Optional convenience: allow clicking a column to drop a disc.
        The task requires typed input; this is an additional usability feature.
        """
        if self.game.game_over:
            return
        x = event.x
        # Ignore clicks outside the board area
        left = self.margin
        right = self.canvas_width - self.margin
        top = self.margin + 20
        bottom = self.canvas_height + 20 - self.margin
        if not (left <= x <= right):
            return
        if not (top <= event.y <= bottom):
            return
        col = int((x - self.margin) // self.cell_size)
        self.attempt_move(col)
    def end_game_feedback(self) -> None:
        """Disable inputs and show final status."""
        self.update_status()
        self.column_entry.configure(state="disabled")
        self.submit_button.configure(state="disabled")
        # Keep reset available
    def reset_game(self) -> None:
        """Reset the game logic and UI."""
        self.game.reset()
        self.column_var.set("")
        self.column_entry.configure(state="normal")
        self.submit_button.configure(state="normal")
        self.draw_board()
        self.update_status()
        self.focus_column_entry()