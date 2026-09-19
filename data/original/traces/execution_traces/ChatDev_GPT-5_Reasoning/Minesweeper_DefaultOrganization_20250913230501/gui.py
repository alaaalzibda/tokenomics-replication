'''
Tkinter-based GUI for the Minesweeper game.
Provides the interface for selecting difficulty, viewing the board,
interacting with cells (left/right click), and viewing game status (timer and mines remaining).
Note on visuals (cross-platform robustness):
- Uses ASCII fallbacks for symbols to ensure they render correctly on systems without emoji fonts.
- Uses 'disabledforeground' to color numbers and mines on disabled (revealed) buttons,
  ensuring colors remain visible across platforms.
'''
import tkinter as tk
from tkinter import messagebox
from game import MinesweeperGame
NUMBER_COLORS = {
    1: "#1e90ff",  # DodgerBlue
    2: "#228B22",  # ForestGreen
    3: "#dc143c",  # Crimson
    4: "#00008b",  # DarkBlue
    5: "#8b0000",  # DarkRed
    6: "#008b8b",  # DarkCyan
    7: "#000000",  # Black
    8: "#696969",  # DimGray
}
# Cross-platform, robust symbols
FLAG_CHAR = "F"   # Distinct and readable without emoji support
MINE_CHAR = "*"   # Simple mine indicator that is always visible
class MinesweeperApp(tk.Frame):
    """
    The main Tkinter application frame for Minesweeper.
    Handles layout, user input, and visual updates.
    """
    DIFFICULTIES = {
        "Beginner": (9, 9, 10),
        "Intermediate": (16, 16, 40),
        "Expert": (30, 16, 99),  # width x height x mines
    }
    def __init__(self, master=None):
        super().__init__(master, bg="#e6e6e6")
        self.master = master
        self.pack(fill="both", expand=True)
        self.current_difficulty = tk.StringVar(value="Beginner")
        self.game = None
        self.buttons = []
        self.timer_id = None
        self._build_controls()
        self._new_game()
    def _build_controls(self):
        top = tk.Frame(self, bg="#f2f2f2", padx=8, pady=8)
        top.pack(side="top", fill="x")
        # Difficulty selector
        tk.Label(top, text="Difficulty:", bg="#f2f2f2").pack(side="left")
        diff_menu = tk.OptionMenu(
            top,
            self.current_difficulty,
            *self.DIFFICULTIES.keys(),
            command=lambda _: self._new_game(),
        )
        diff_menu.config(width=12)
        diff_menu.pack(side="left", padx=(4, 12))
        # Reset button
        reset_btn = tk.Button(top, text="New Game", command=self._new_game)
        reset_btn.pack(side="left")
        # Spacer
        tk.Label(top, text="   ", bg="#f2f2f2").pack(side="left")
        # Mines remaining label
        self.mines_label = tk.Label(top, text="Mines: 0", font=("Arial", 11, "bold"), bg="#f2f2f2")
        self.mines_label.pack(side="left")
        # Spacer
        tk.Label(top, text="   ", bg="#f2f2f2").pack(side="left")
        # Timer label
        self.timer_label = tk.Label(top, text="Time: 0", font=("Arial", 11, "bold"), bg="#f2f2f2")
        self.timer_label.pack(side="left")
        # Board container
        self.board_frame = tk.Frame(self, bg="#bdbdbd", padx=8, pady=8)
        self.board_frame.pack(side="top", expand=True)
        # Footer
        footer = tk.Frame(self, bg="#f2f2f2", padx=8, pady=4)
        footer.pack(side="bottom", fill="x")
        tk.Label(
            footer,
            text="Left-click: reveal | Right-click / Middle-click / Ctrl+Click: flag/unflag",
            bg="#f2f2f2",
        ).pack(side="left")
    def _new_game(self):
        # Cancel timer updates if running
        if self.timer_id is not None:
            self.after_cancel(self.timer_id)
            self.timer_id = None
        width, height, mines = self.DIFFICULTIES[self.current_difficulty.get()]
        self.game = MinesweeperGame(width, height, mines)
        # Rebuild grid of buttons
        for child in self.board_frame.winfo_children():
            child.destroy()
        self.buttons = [[None for _ in range(width)] for _ in range(height)]
        for y in range(height):
            for x in range(width):
                btn = tk.Button(
                    self.board_frame,
                    width=2,
                    height=1,
                    text="",
                    relief="raised",
                    bg="#d0d0d0",
                    activebackground="#c8c8c8",
                    font=("Arial", 12, "bold"),
                    disabledforeground="#404040",  # default; may be overridden per cell
                )
                btn.grid(row=y, column=x, sticky="nsew")
                # Click bindings: include platform-friendly aliases for flagging
                btn.bind("<Button-1>", lambda e, cx=x, cy=y: self._on_left_click(cx, cy))
                btn.bind("<Button-3>", lambda e, cx=x, cy=y: self._on_right_click(cx, cy))          # Right-click
                btn.bind("<Button-2>", lambda e, cx=x, cy=y: self._on_right_click(cx, cy))          # Middle/right on some Macs
                btn.bind("<Control-Button-1>", lambda e, cx=x, cy=y: self._on_right_click(cx, cy))  # Ctrl+Click fallback
                self.buttons[y][x] = btn
        # Configure grid weights for responsiveness
        for y in range(height):
            self.board_frame.rowconfigure(y, weight=1)
        for x in range(width):
            self.board_frame.columnconfigure(x, weight=1)
        self._update_mines_label()
        self._update_timer_label(force_zero=True)
    def _on_left_click(self, x, y):
        if self.game.state != "playing":
            return
        result, changed, exploded_at = self.game.left_click(x, y)
        # Start timer loop on first reveal
        if self.game.started and self.timer_id is None and self.game.state == "playing":
            self._schedule_timer_tick()
        self._refresh_cells(changed, exploded_at)
        if result == "lost":
            self._reveal_all()
            messagebox.showinfo("Minesweeper", "Boom! You hit a mine. Game over.")
        elif result == "won":
            self._reveal_all()
            messagebox.showinfo("Minesweeper", "Congratulations! You cleared the board.")
        self._update_mines_label()
    def _on_right_click(self, x, y):
        if self.game.state != "playing":
            return
        self.game.right_click(x, y)
        # Update just this button
        self._refresh_cells({(x, y)}, None)
        self._update_mines_label()
    def _refresh_cells(self, coords, exploded_at):
        """
        Update the appearance of cells in coords. If exploded_at is provided, color it specially.
        """
        for (x, y) in coords:
            cell = self.game.board.get_cell(x, y)
            btn = self.buttons[y][x]
            if cell.revealed:
                btn.config(relief="sunken", bg="#f2f2f2", state="disabled")
                if cell.has_mine:
                    if exploded_at == (x, y):
                        btn.config(bg="#ff4d4d")  # highlight the exploded mine
                    # Ensure mine symbol is readable on disabled button
                    btn.config(text=MINE_CHAR, disabledforeground="#000000")
                else:
                    n = cell.adjacent
                    if n > 0:
                        # Use disabledforeground so color shows on disabled button
                        btn.config(text=str(n), disabledforeground=NUMBER_COLORS.get(n, "#000000"))
                    else:
                        btn.config(text="")
            else:
                # Hidden cell
                if cell.flagged:
                    btn.config(text=FLAG_CHAR, fg="#d40000", bg="#ffd6d6", relief="raised", state="normal")
                else:
                    btn.config(text="", bg="#d0d0d0", relief="raised", state="normal")
    def _reveal_all(self):
        """
        Reveal all cells to show final state (mines and numbers).
        """
        width, height = self.game.board.width, self.game.board.height
        all_coords = {(x, y) for y in range(height) for x in range(width)}
        # Mark all mines revealed
        for y in range(height):
            for x in range(width):
                cell = self.game.board.get_cell(x, y)
                if cell.has_mine:
                    cell.revealed = True
        self._refresh_cells(all_coords, exploded_at=self.game.exploded_at)
    def _update_mines_label(self):
        remaining = self.game.board.num_mines - self.game.board.flag_count()
        self.mines_label.config(text=f"Mines: {remaining}")
    def _schedule_timer_tick(self):
        """
        Update the timer label and schedule the next tick only while playing.
        When the game ends, stop scheduling and show the final frozen time.
        """
        if self.game.state != "playing":
            self.timer_id = None
            self._update_timer_label()  # show the final frozen time
            return
        self._update_timer_label()
        self.timer_id = self.after(1000, self._schedule_timer_tick)
    def _update_timer_label(self, force_zero=False):
        if force_zero:
            self.timer_label.config(text="Time: 0")
            return
        elapsed = int(self.game.elapsed_time())
        self.timer_label.config(text=f"Time: {elapsed}")