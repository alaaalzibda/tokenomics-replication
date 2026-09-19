'''
Graphical User Interface for the Tic-Tac-Toe game using Tkinter.
This module defines the TicTacToeGUI class which manages the visual
representation of the game, handles user interactions, and communicates
with the TicTacToeGame logic class.
Features:
- 3x3 grid of buttons for moves.
- Status label indicating current player's turn or game result.
- New Game and Quit controls.
- Menu bar with keyboard shortcuts (Ctrl+N for New Game, Ctrl+Q for Quit).
- Highlights the winning line on victory.
- Alternates the starting player on each new game for fairness.
'''
import tkinter as tk
from tkinter import messagebox
from typing import List, Optional, Tuple
from game_logic import TicTacToeGame
from constants import GRID_SIZE, SYMBOL_X, SYMBOL_O, COLORS, FONTS, WINDOW_TITLE, APP_VERSION
class TicTacToeGUI:
    """Tkinter-based GUI for the Tic-Tac-Toe game."""
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.game = TicTacToeGame()
        self.buttons: List[List[tk.Button]] = []
        # Containers
        self.status_label: Optional[tk.Label] = None
        self.grid_frame: Optional[tk.Frame] = None
        self.control_frame: Optional[tk.Frame] = None
    def build_ui(self) -> None:
        """Create all UI components and layout."""
        # Menu bar
        self._build_menu()
        # Status area
        status_frame = tk.Frame(self.root, bg=COLORS['bg'])
        status_frame.pack(padx=12, pady=(12, 6), fill='x')
        self.status_label = tk.Label(
            status_frame,
            text="",
            font=FONTS['status'],
            bg=COLORS['bg'],
            fg=COLORS['status_fg']
        )
        self.status_label.pack(anchor='center')
        # Grid area
        self.grid_frame = tk.Frame(self.root, bg=COLORS['grid_bg'])
        self.grid_frame.pack(padx=12, pady=6)
        self._build_grid_buttons()
        # Control area
        self.control_frame = tk.Frame(self.root, bg=COLORS['bg'])
        self.control_frame.pack(padx=12, pady=(6, 12), fill='x')
        reset_btn = tk.Button(
            self.control_frame,
            text="New Game",
            font=FONTS['control'],
            bg=COLORS['button_bg'],
            fg=COLORS['button_fg'],
            activebackground=COLORS['button_bg'],
            activeforeground=COLORS['button_fg'],
            command=self.reset_game
        )
        reset_btn.pack(side='left', padx=(0, 8))
        quit_btn = tk.Button(
            self.control_frame,
            text="Quit",
            font=FONTS['control'],
            bg=COLORS['button_bg'],
            fg=COLORS['button_fg'],
            activebackground=COLORS['button_bg'],
            activeforeground=COLORS['button_fg'],
            command=self.root.destroy
        )
        quit_btn.pack(side='left')
        # Keyboard shortcuts
        self.root.bind('<Control-n>', lambda e: self.reset_game())
        self.root.bind('<Control-q>', lambda e: self.root.destroy())
        # Initialize status text
        self.update_status()
    def _build_menu(self) -> None:
        """Create the application menu bar."""
        menu_bar = tk.Menu(self.root)
        game_menu = tk.Menu(menu_bar, tearoff=0)
        game_menu.add_command(label="New Game", command=self.reset_game, accelerator="Ctrl+N")
        game_menu.add_separator()
        game_menu.add_command(label="Quit", command=self.root.destroy, accelerator="Ctrl+Q")
        menu_bar.add_cascade(label="Game", menu=game_menu)
        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        menu_bar.add_cascade(label="Help", menu=help_menu)
        self.root.config(menu=menu_bar)
    def _build_grid_buttons(self) -> None:
        """Create the 3x3 grid of buttons."""
        assert self.grid_frame is not None
        self.buttons = []
        for r in range(GRID_SIZE):
            row_buttons: List[tk.Button] = []
            for c in range(GRID_SIZE):
                btn = tk.Button(
                    self.grid_frame,
                    text="",
                    width=4,
                    height=2,
                    font=FONTS['cell'],
                    bg=COLORS['button_bg'],
                    fg=COLORS['button_fg'],
                    activebackground=COLORS['button_bg'],
                    activeforeground=COLORS['button_fg'],
                    relief='raised',
                    borderwidth=2,
                    command=lambda rr=r, cc=c: self.on_cell_click(rr, cc)
                )
                btn.grid(row=r, column=c, padx=6, pady=6, sticky='nsew')
                row_buttons.append(btn)
            self.buttons.append(row_buttons)
        # Make grid cells expand evenly (even though window is fixed)
        for i in range(GRID_SIZE):
            self.grid_frame.grid_rowconfigure(i, weight=1, uniform="row")
            self.grid_frame.grid_columnconfigure(i, weight=1, uniform="col")
    def on_cell_click(self, row: int, col: int) -> None:
        """Handle a click on a cell button."""
        # Ignore clicks if game already ended
        if self.game.winner is not None or self.game.is_draw():
            return
        moved = self.game.make_move(row, col)
        if not moved:
            # Either occupied cell or invalid move; do nothing
            return
        # Update the clicked button to show the symbol
        symbol = self.game.get_cell(row, col)
        btn = self.buttons[row][col]
        btn.config(text=symbol)
        self._apply_symbol_style(btn, symbol)
        # If the game is over, handle result; otherwise update status
        if self.game.winner is not None:
            self.highlight_winning_line()
            self.disable_board()
            self.update_status()
            messagebox.showinfo("Game Over", f"Player {self.game.winner} wins!")
        elif self.game.is_draw():
            self.disable_board()
            self.update_status()
            messagebox.showinfo("Game Over", "It's a draw!")
        else:
            self.update_status()
    def update_status(self) -> None:
        """Update the status label based on game state."""
        if not self.status_label:
            return
        if self.game.winner is not None:
            self.status_label.config(
                text=f"Player {self.game.winner} wins!",
                fg=COLORS['x_fg'] if self.game.winner == SYMBOL_X else COLORS['o_fg']
            )
        elif self.game.is_draw():
            self.status_label.config(text="It's a draw. Start a new game!", fg=COLORS['status_fg'])
        else:
            # Indicate whose turn it is, with matching color
            color = COLORS['x_fg'] if self.game.current_player == SYMBOL_X else COLORS['o_fg']
            self.status_label.config(text=f"Turn: Player {self.game.current_player}", fg=color)
    def highlight_winning_line(self) -> None:
        """Highlight the winning line cells if there is a winner."""
        if self.game.winning_line is None:
            return
        for (r, c) in self.game.winning_line:
            btn = self.buttons[r][c]
            btn.config(bg=COLORS['highlight'])
    def _apply_symbol_style(self, button: tk.Button, symbol: str) -> None:
        """Apply per-symbol foreground color."""
        if symbol == SYMBOL_X:
            button.config(fg=COLORS['x_fg'])
        elif symbol == SYMBOL_O:
            button.config(fg=COLORS['o_fg'])
        else:
            button.config(fg=COLORS['button_fg'])
    def disable_board(self) -> None:
        """Disable all grid buttons."""
        for row in self.buttons:
            for btn in row:
                btn.config(state='disabled', disabledforeground=COLORS['button_disabled_fg'])
    def enable_board(self) -> None:
        """Enable all grid buttons."""
        for r, row in enumerate(self.buttons):
            for c, btn in enumerate(row):
                btn.config(state='normal')
                # Re-apply text and symbol style (in case of reset or resume)
                symbol = self.game.get_cell(r, c)
                btn.config(text=symbol if symbol else "")
                self._apply_symbol_style(btn, symbol)
                # Reset background (remove any highlight)
                btn.config(bg=COLORS['button_bg'])
    def reset_game(self) -> None:
        """Reset the game state and UI to start a new match."""
        self.game.reset(alternate=True)
        # Clear button texts and styles
        for row in self.buttons:
            for btn in row:
                btn.config(text="", bg=COLORS['button_bg'], fg=COLORS['button_fg'], state='normal')
        self.update_status()
    def show_about(self) -> None:
        """Show an About dialog."""
        message = (
            f"{WINDOW_TITLE}\n"
            f"Version {APP_VERSION}\n\n"
            "Two-player Tic-Tac-Toe.\n"
            "- Click a cell to place your mark.\n"
            "- Players alternate as X and O.\n"
            "- First to get 3 in a row wins.\n"
            "- Use 'New Game' (Ctrl+N) to start over."
        )
        messagebox.showinfo("About", message)