'''
Tkinter GUI for the Strands puzzle. Handles rendering the grid, mouse interactions
for selecting words by dragging across adjacent cells, feedback coloring, status,
and hint logic.
'''
import tkinter as tk
from tkinter import messagebox
# Support running whether this module is inside a package or at project root.
try:
    from .game import GameState
except Exception:
    from game import GameState
CELL_SIZE = 52
FONT = ("Helvetica", 16, "bold")
COLOR_BG = "#fafafa"
COLOR_CELL_BG = "#ffffff"
COLOR_CELL_BORDER = "#cccccc"
COLOR_CELL_TEXT = "#333333"
COLOR_TEMP = "#b2dfdb"      # teal-ish for current selection
COLOR_THEME = "#64b5f6"     # blue for themed words
COLOR_SPANGRAM = "#ffd54f"  # yellow for spangram
COLOR_INVALID = "#ffcdd2"   # light red flash for invalid
COLOR_NON_THEME = "#c5e1a5" # light green flash for valid non-theme (transient)
MIN_NON_THEME_LEN = 4
class StrandsApp:
    def __init__(self, root: tk.Tk, puzzle):
        self.root = root
        self.root.title("Strands - Programming Languages Edition")
        self.puzzle = puzzle
        self.game = GameState(puzzle)
        self.grid_frame = None
        self.status_frame = None
        self.buttons = {}  # (r,c) -> Button
        self.cell_states = {}  # (r,c) -> {'claimed': bool, 'type': 'theme'|'spangram'|None, 'word': str|None}
        # drag/selection state
        self.dragging = False
        self.selection = []  # list of (r,c)
        self.selection_set = set()
        self._build_ui()
        self._populate_grid()
        self.update_status()
    def _build_ui(self):
        self.root.configure(bg=COLOR_BG)
        title = tk.Label(self.root, text=f"Theme: {self.puzzle.theme}", font=("Helvetica", 14, "bold"), bg=COLOR_BG)
        title.pack(pady=(10, 5))
        self.grid_frame = tk.Frame(self.root, bg=COLOR_BG, bd=0, highlightthickness=0)
        self.grid_frame.pack(padx=10, pady=10)
        for r in range(self.puzzle.rows):
            self.grid_frame.grid_rowconfigure(r, weight=1)
        for c in range(self.puzzle.cols):
            self.grid_frame.grid_columnconfigure(c, weight=1)
        # Status and Controls
        self.status_frame = tk.Frame(self.root, bg=COLOR_BG)
        self.status_frame.pack(fill="x", padx=10, pady=(0, 10))
        self.found_label = tk.Label(self.status_frame, text="", font=("Helvetica", 12), bg=COLOR_BG)
        self.found_label.pack(side="left")
        self.hints_label = tk.Label(self.status_frame, text="", font=("Helvetica", 12), bg=COLOR_BG)
        self.hints_label.pack(side="left", padx=(15, 0))
        controls = tk.Frame(self.root, bg=COLOR_BG)
        controls.pack(pady=(0, 10))
        self.hint_button = tk.Button(controls, text="Use Hint", command=self.on_hint, bg="#eeeeee")
        self.hint_button.pack(side="left", padx=5)
        self.reset_button = tk.Button(controls, text="Reset Progress", command=self.on_reset, bg="#eeeeee")
        self.reset_button.pack(side="left", padx=5)
        self.show_words_button = tk.Button(controls, text="Show Remaining Words", command=self.on_show_remaining, bg="#eeeeee")
        self.show_words_button.pack(side="left", padx=5)
        # Bind global mouse release to ensure ending drag if released outside a cell
        self.root.bind("<ButtonRelease-1>", self._global_mouse_up)
    def _populate_grid(self):
        for r in range(self.puzzle.rows):
            for c in range(self.puzzle.cols):
                letter = self.puzzle.get_letter(r, c)
                btn = tk.Label(self.grid_frame, text=letter, width=3, height=1, font=FONT,
                               bd=1, relief="solid", bg=COLOR_CELL_BG, fg=COLOR_CELL_TEXT)
                btn.grid(row=r, column=c, padx=2, pady=2, sticky="nsew")
                # mouse events
                btn.bind("<ButtonPress-1>", lambda e, rr=r, cc=c: self.start_drag(rr, cc))
                btn.bind("<Enter>", lambda e, rr=r, cc=c: self.enter_cell(rr, cc))
                btn.bind("<ButtonRelease-1>", lambda e, rr=r, cc=c: self.end_drag())
                self.buttons[(r, c)] = btn
                self.cell_states[(r, c)] = {'claimed': False, 'type': None, 'word': None}
    def on_hint(self):
        if self.game.hints <= 0:
            messagebox.showinfo("No hints", "You don't have any hints yet. Find 3 non-theme words to earn a hint.")
            return
        revealed = self.game.reveal_hint()
        if not revealed:
            messagebox.showinfo("Hints", "All themed words are already found!")
            return
        word, coords, word_type = revealed
        self.apply_claim(coords, word_type, word)
        self.update_status()
        if self.game.is_completed():
            self._show_completion()
    def on_reset(self):
        if not messagebox.askyesno("Reset", "Reset your current progress?"):
            return
        # Reset app state and game state to the initial
        self.game = GameState(self.puzzle)
        self.selection.clear()
        self.selection_set.clear()
        self.dragging = False
        # Reset cell visuals
        for coord, btn in self.buttons.items():
            btn.configure(bg=COLOR_CELL_BG, fg=COLOR_CELL_TEXT)
            self.cell_states[coord] = {'claimed': False, 'type': None, 'word': None}
        self.update_status()
    def on_show_remaining(self):
        remaining = [w for w in self.puzzle.theme_words if w not in self.game.found_words]
        if self.puzzle.spangram not in self.game.found_words:
            remaining = [f"(spangram) {self.puzzle.spangram}"] + remaining
        if not remaining:
            messagebox.showinfo("Remaining Words", "All words found!")
            return
        # Show as message
        message = "Words remaining:\n" + "\n".join(remaining)
        messagebox.showinfo("Remaining Words", message)
    def start_drag(self, r, c):
        # If this cell is already claimed, don't start selection from it
        if not self.game.can_select_cell((r, c)):
            return
        self.dragging = True
        self.selection = [(r, c)]
        self.selection_set = {(r, c)}
        self._color_cell((r, c), COLOR_TEMP)
    def enter_cell(self, r, c):
        if not self.dragging:
            return
        coord = (r, c)
        if coord in self.selection_set:
            return  # no repeats
        if not self.game.can_select_cell(coord):
            return
        if not self.selection:
            return
        last = self.selection[-1]
        if not self.game.is_adjacent(last, coord):
            return
        # Append
        self.selection.append(coord)
        self.selection_set.add(coord)
        self._color_cell(coord, COLOR_TEMP)
    def end_drag(self):
        if not self.dragging:
            return
        self.dragging = False
        # Evaluate the selection
        result = self.game.try_commit_selection(self.selection)
        # Reset temporary highlight by default
        temp_coords = list(self.selection)
        self.selection.clear()
        self.selection_set.clear()
        if result['type'] == 'spangram':
            coords = result['coords']
            word = result['word']
            self.apply_claim(coords, 'spangram', word)
        elif result['type'] == 'theme':
            coords = result['coords']
            word = result['word']
            self.apply_claim(coords, 'theme', word)
        elif result['type'] == 'non-theme':
            # flash green briefly then restore
            self._flash_cells(temp_coords, COLOR_NON_THEME)
        else:
            # invalid selection -> flash red
            self._flash_cells(temp_coords, COLOR_INVALID)
        self.update_status()
        if self.game.is_completed():
            self._show_completion()
    def _global_mouse_up(self, _event):
        # Ends a drag if release happens outside a cell
        if self.dragging:
            self.end_drag()
    def _color_cell(self, coord, color, text_color=COLOR_CELL_TEXT):
        btn = self.buttons.get(coord)
        if btn:
            btn.configure(bg=color, fg=text_color)
    def _flash_cells(self, coords, color):
        # Temporarily paint then restore unclaimed cell colors
        for coord in coords:
            if not self.cell_states[coord]['claimed']:
                self._color_cell(coord, color)
        # After delay, restore
        self.root.after(250, lambda: self._restore_temp_colors(coords))
    def _restore_temp_colors(self, coords):
        for coord in coords:
            if not self.cell_states[coord]['claimed']:
                self._color_cell(coord, COLOR_CELL_BG, COLOR_CELL_TEXT)
    def apply_claim(self, coords, word_type, word):
        color = COLOR_SPANGRAM if word_type == 'spangram' else COLOR_THEME
        text_color = "#000000"
        for coord in coords:
            self.cell_states[coord] = {'claimed': True, 'type': word_type, 'word': word}
            self._color_cell(coord, color, text_color)
    def update_status(self):
        total_theme = len(self.puzzle.theme_words)
        found_theme = sum(1 for w in self.puzzle.theme_words if w in self.game.found_words)
        spangram_done = (self.puzzle.spangram in self.game.found_words)
        self.found_label.configure(
            text=f"Found: {found_theme}/{total_theme} themes; Spangram: {'Yes' if spangram_done else 'No'}"
        )
        self.hints_label.configure(text=f"Hints: {self.game.hints}; Non-theme words: {len(self.game.non_theme_words)}")
    def _show_completion(self):
        messagebox.showinfo("Congratulations!", "You completed the puzzle and filled the board!")