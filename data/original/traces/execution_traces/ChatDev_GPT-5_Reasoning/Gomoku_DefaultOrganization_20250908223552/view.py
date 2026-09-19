'''
Tkinter-based GUI for the Gomoku game. Provides a graphical board, control buttons, and status display.
Captures mouse clicks to place stones and renders the board state, including a highlight for winning lines.
'''
import tkinter as tk
from tkinter import messagebox
from typing import Optional, List, Tuple
Coord = Tuple[int, int]
class BoardCanvas(tk.Canvas):
    """
    Canvas widget that draws the Gomoku board grid, stones, last move marker,
    and highlights the winning line when the game ends.
    """
    def __init__(
        self,
        master,
        controller,
        size: int,
        cell_size: int = 40,
        margin: int = 30,
        **kwargs
    ):
        self.controller = controller
        self.size = size
        self.cell_size = cell_size
        self.margin = margin
        # Canvas dimensions: grid has (size - 1) intervals between lines
        grid_pixels = (size - 1) * cell_size
        width = margin * 2 + grid_pixels
        height = margin * 2 + grid_pixels
        super().__init__(master, width=width, height=height, bg="#f0d9b5", highlightthickness=0, **kwargs)
        self.bind("<Button-1>", self.on_click)
    def redraw(self) -> None:
        """Redraw the entire board: grid, stones, last move marker, and winner highlight."""
        self.delete("all")
        self.draw_grid()
        self.draw_stones()
        # Draw winning highlight if exists
        if getattr(self.controller, "winning_coords", None):
            self.draw_winning_highlight(self.controller.winning_coords)
    def draw_grid(self) -> None:
        """Draw the 15x15 grid lines."""
        size = self.size
        m = self.margin
        cs = self.cell_size
        # Board lines
        line_color = "#6b4f2a"
        for i in range(size):
            # horizontal line y constant
            y = m + i * cs
            self.create_line(m, y, m + (size - 1) * cs, y, fill=line_color)
            # vertical line x constant
            x = m + i * cs
            self.create_line(x, m, x, m + (size - 1) * cs, fill=line_color)
        # Star points typical for 15x15: (3,3), (3,11), (7,7), (11,3), (11,11)
        star_points = [(3, 3), (3, 11), (7, 7), (11, 3), (11, 11)]
        for r, c in star_points:
            cx, cy = self.cell_center(r, c)
            self.create_oval(cx - 3, cy - 3, cx + 3, cy + 3, fill=line_color, outline=line_color)
    def draw_stones(self) -> None:
        """Draw stones from the model and a marker on the last move."""
        board = self.controller.board
        cs = self.cell_size
        radius = cs // 2 - 4  # stone radius
        outline = "#333333"
        last = board.last_move()
        last_rc = (last[0], last[1]) if last else None
        for r in range(board.size):
            for c in range(board.size):
                cell = board.get_cell(r, c)
                if cell == 0:
                    continue
                cx, cy = self.cell_center(r, c)
                if cell == 1:
                    fill = "#111111"
                else:
                    fill = "#eeeeee"
                self.create_oval(
                    cx - radius,
                    cy - radius,
                    cx + radius,
                    cy + radius,
                    fill=fill,
                    outline=outline,
                    width=2,
                )
                # Last move marker: small orange dot on top
                if last_rc and (r, c) == last_rc and not self.controller.game_over:
                    self.create_oval(cx - 4, cy - 4, cx + 4, cy + 4, fill="#ff6f00", outline="")
    def draw_winning_highlight(self, coords: List[Coord]) -> None:
        """Draw a thick red line through the winning five stones."""
        if not coords:
            return
        # Sort coords by line order from first to last
        # They should already be contiguous; we can draw a polyline
        points = []
        for r, c in coords:
            x, y = self.cell_center(r, c)
            points.extend([x, y])
        # Draw a slightly transparent red line by overlaying two lines
        self.create_line(*points, fill="#c62828", width=6, capstyle=tk.ROUND)
        self.create_line(*points, fill="#ef5350", width=2, capstyle=tk.ROUND)
    def pixel_to_cell(self, x: float, y: float) -> Optional[Coord]:
        """
        Convert pixel (x, y) to the nearest board intersection (row, col).
        Returns None if the click is too far from any intersection.
        """
        m = self.margin
        cs = self.cell_size
        # Translate to grid coords
        col_f = (x - m) / cs
        row_f = (y - m) / cs
        col = int(round(col_f))
        row = int(round(row_f))
        if not (0 <= row < self.size and 0 <= col < self.size):
            return None
        # Ensure the click is near an intersection within a tolerance
        cx, cy = self.cell_center(row, col)
        dx = abs(x - cx)
        dy = abs(y - cy)
        tolerance = cs * 0.4  # generous tolerance
        if dx <= tolerance and dy <= tolerance:
            return (row, col)
        return None
    def cell_center(self, row: int, col: int) -> Tuple[float, float]:
        """Return the pixel center of the given board cell."""
        x = self.margin + col * self.cell_size
        y = self.margin + row * self.cell_size
        return (x, y)
    def on_click(self, event) -> None:
        """Handle mouse left-click to place a stone."""
        if self.controller.game_over:
            return
        cell = self.pixel_to_cell(event.x, event.y)
        if cell is None:
            return
        row, col = cell
        self.controller.handle_board_click(row, col)
class GomokuApp(tk.Tk):
    """
    Top-level application window for Gomoku. Includes the board canvas, control buttons, and a status bar.
    """
    def __init__(self, controller) -> None:
        super().__init__()
        self.title("Gomoku (Five in a Row) - 15x15")
        self.resizable(False, False)
        self.controller = controller
        # Layout frames
        self.board_frame = tk.Frame(self)
        self.board_frame.pack(side=tk.TOP, padx=10, pady=10)
        self.controls_frame = tk.Frame(self)
        self.controls_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=(0, 10))
        # Board Canvas
        self.canvas = BoardCanvas(
            self.board_frame,
            controller=self.controller,
            size=self.controller.board.size,
            cell_size=40,
            margin=30,
        )
        self.canvas.pack()
        # Controls
        self.new_btn = tk.Button(self.controls_frame, text="New Game", command=self.controller.start_new_game)
        self.undo_btn = tk.Button(self.controls_frame, text="Undo", command=self.controller.undo_move)
        self.redo_btn = tk.Button(self.controls_frame, text="Redo", command=self.controller.redo_move)
        self.new_btn.pack(side=tk.LEFT, padx=(0, 8))
        self.undo_btn.pack(side=tk.LEFT, padx=(0, 8))
        self.redo_btn.pack(side=tk.LEFT, padx=(0, 8))
        # Status label
        self.status_var = tk.StringVar(value=self.controller.get_status_text())
        self.status_label = tk.Label(self, textvariable=self.status_var, anchor="w", font=("Segoe UI", 11))
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=(0, 10))
        # Keyboard shortcuts
        self.bind_all("<Control-n>", lambda e: self.controller.start_new_game())
        self.bind_all("<Control-z>", lambda e: self.controller.undo_move())
        self.bind_all("<Control-y>", lambda e: self.controller.redo_move())
        # Initial draw
        self.refresh()
    def refresh(self) -> None:
        """Refresh the canvas drawing and update the status label."""
        self.canvas.redraw()
        self.status_var.set(self.controller.get_status_text())
    def show_winner(self, winner: int, winning_coords: Optional[List[Coord]]) -> None:
        """
        Show a message box indicating the winner and ensure the winning line is drawn.
        """
        if winner == 1:
            msg = "Black wins!"
        elif winner == 2:
            msg = "White wins!"
        else:
            msg = "Draw."
        # Ensure highlight is drawn
        self.canvas.redraw()
        # Show result message
        messagebox.showinfo("Game Over", msg)