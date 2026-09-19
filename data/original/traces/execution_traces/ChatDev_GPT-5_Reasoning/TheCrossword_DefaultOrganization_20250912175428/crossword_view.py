'''
Crossword view: builds the Tkinter GUI, displays the grid and clues,
and provides input controls for entering answers by clue number and direction.
The view is decoupled from the model; it exposes methods to:
- Update the grid display
- Render clues for across and down
- Show status messages
- Retrieve/clear user input
- Bind submit and reset handlers
'''
import tkinter as tk
from tkinter import ttk
from typing import List, Tuple, Callable, Optional
from crossword_model import CrosswordEntry
class CrosswordView:
    def __init__(self, root: tk.Tk, title: str = "Crossword"):
        self.root = root
        self.root.title(title)
        self.root.geometry("900x600")
        self.root.minsize(800, 520)
        # Top-level layout: left grid frame, right side controls and clues
        self.main = ttk.Frame(self.root, padding=10)
        self.main.pack(fill=tk.BOTH, expand=True)
        self.left_frame = ttk.Frame(self.main)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.right_frame = ttk.Frame(self.main)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        # Grid frame
        self.grid_frame = ttk.Frame(self.left_frame)
        self.grid_frame.pack(fill=tk.BOTH, expand=True)
        # Controls frame
        self.controls_frame = ttk.LabelFrame(self.right_frame, text="Enter Answer", padding=10)
        self.controls_frame.pack(fill=tk.X, pady=(0, 10))
        # Clues frame
        self.clues_frame = ttk.LabelFrame(self.right_frame, text="Clues", padding=10)
        self.clues_frame.pack(fill=tk.BOTH, expand=True)
        # Status
        self.status_var = tk.StringVar(value="Welcome! Select a clue and enter its answer.")
        self.status_label = ttk.Label(self.right_frame, textvariable=self.status_var, foreground="#333")
        self.status_label.pack(fill=tk.X, pady=(8, 0))
        # Initialize grid placeholders
        self.cell_labels: List[List[tk.Label]] = []
        self.rows = 0
        self.cols = 0
        # Controls
        self.number_var = tk.StringVar()
        self.direction_var = tk.StringVar(value="A")
        self.answer_var = tk.StringVar()
        number_row = ttk.Frame(self.controls_frame)
        number_row.pack(fill=tk.X, pady=4)
        ttk.Label(number_row, text="Clue number:").pack(side=tk.LEFT)
        self.number_spin = tk.Spinbox(
            number_row, from_=1, to=99, textvariable=self.number_var, width=6, justify=tk.RIGHT
        )
        self.number_spin.pack(side=tk.LEFT, padx=(8, 0))
        dir_row = ttk.Frame(self.controls_frame)
        dir_row.pack(fill=tk.X, pady=4)
        ttk.Label(dir_row, text="Direction:").pack(side=tk.LEFT)
        self.dir_across_rb = ttk.Radiobutton(
            dir_row, text="Across", variable=self.direction_var, value="A"
        )
        self.dir_down_rb = ttk.Radiobutton(
            dir_row, text="Down", variable=self.direction_var, value="D"
        )
        self.dir_across_rb.pack(side=tk.LEFT, padx=(8, 0))
        self.dir_down_rb.pack(side=tk.LEFT, padx=(8, 0))
        ans_row = ttk.Frame(self.controls_frame)
        ans_row.pack(fill=tk.X, pady=4)
        ttk.Label(ans_row, text="Answer:").pack(side=tk.LEFT)
        self.answer_entry = ttk.Entry(ans_row, textvariable=self.answer_var)
        self.answer_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(8, 0))
        btn_row = ttk.Frame(self.controls_frame)
        btn_row.pack(fill=tk.X, pady=8)
        self.submit_btn = ttk.Button(btn_row, text="Submit")
        self.submit_btn.pack(side=tk.LEFT)
        self.reset_btn = ttk.Button(btn_row, text="Reset")
        self.reset_btn.pack(side=tk.LEFT, padx=8)
        # Clues display (two text widgets)
        self.across_text = tk.Text(self.clues_frame, height=12, wrap=tk.WORD)
        self.down_text = tk.Text(self.clues_frame, height=12, wrap=tk.WORD)
        # Labels for the sections
        ttk.Label(self.clues_frame, text="Across").pack(anchor=tk.W)
        self.across_text.pack(fill=tk.BOTH, expand=True, pady=(0, 8))
        ttk.Label(self.clues_frame, text="Down").pack(anchor=tk.W)
        self.down_text.pack(fill=tk.BOTH, expand=True)
        # Style text widgets as read-only
        for t in (self.across_text, self.down_text):
            t.configure(state=tk.DISABLED)
            t.configure(background="#fafafa")
        # Bind Enter key for submitting answer
        self.answer_entry.bind("<Return>", lambda e: self._on_submit_enter())
        # callbacks placeholders
        self._submit_cb: Optional[Callable[[], None]] = None
        self._reset_cb: Optional[Callable[[], None]] = None
        # Focus the answer field initially for convenience
        self.answer_entry.focus_set()
    def _on_submit_enter(self):
        if self._submit_cb:
            self._submit_cb()
    def set_number_range(self, min_num: int, max_num: int):
        try:
            self.number_spin.config(from_=min_num, to=max_num)
        except tk.TclError:
            # Fallback if Spinbox not ready, set text value only
            pass
    def build_grid(self, rows: int, cols: int):
        # Clear any previous grid
        for child in self.grid_frame.winfo_children():
            child.destroy()
        self.cell_labels = []
        self.rows = rows
        self.cols = cols
        # Build new grid of labels
        for r in range(rows):
            row_labels: List[tk.Label] = []
            for c in range(cols):
                lbl = tk.Label(
                    self.grid_frame,
                    text="",
                    width=3,
                    height=1,
                    borderwidth=1,
                    relief="solid",
                    font=("Helvetica", 18, "bold"),
                    bg="white",
                )
                lbl.grid(row=r, column=c, sticky="nsew", padx=1, pady=1)
                row_labels.append(lbl)
            self.cell_labels.append(row_labels)
        # Make grid cells expand uniformly
        for r in range(rows):
            self.grid_frame.rowconfigure(r, weight=1)
        for c in range(cols):
            self.grid_frame.columnconfigure(c, weight=1)
    def update_grid(self, cell_value_at: Callable[[int, int], str]):
        for r in range(self.rows):
            for c in range(self.cols):
                val = cell_value_at(r, c)
                lbl = self.cell_labels[r][c]
                if val == "#":
                    lbl.configure(text="", bg="black")
                else:
                    lbl.configure(text=val if val else "", bg="white")
    def render_clues(self, across_entries: List[CrosswordEntry], down_entries: List[CrosswordEntry]):
        across_str_lines = []
        for e in across_entries:
            mark = "✓ " if e.filled else "  "
            across_str_lines.append(f"{mark}{e.number}A ({e.length}): {e.clue}")
        down_str_lines = []
        for e in down_entries:
            mark = "✓ " if e.filled else "  "
            down_str_lines.append(f"{mark}{e.number}D ({e.length}): {e.clue}")
        self._set_text(self.across_text, "\n".join(across_str_lines) if across_str_lines else "(none)")
        self._set_text(self.down_text, "\n".join(down_str_lines) if down_str_lines else "(none)")
    def _set_text(self, text_widget: tk.Text, content: str):
        text_widget.configure(state=tk.NORMAL)
        text_widget.delete("1.0", tk.END)
        text_widget.insert(tk.END, content)
        text_widget.configure(state=tk.DISABLED)
    def get_input(self) -> Tuple[Optional[int], str, str]:
        num_str = self.number_var.get().strip()
        try:
            number = int(num_str)
        except ValueError:
            number = None
        direction = (self.direction_var.get() or "A").upper()
        answer = self.answer_var.get().strip()
        return number, direction, answer
    def clear_answer_field(self):
        self.answer_var.set("")
        self.answer_entry.focus_set()
        self.answer_entry.icursor(tk.END)
    def set_status(self, message: str, ok: bool = True):
        self.status_var.set(message)
        self.status_label.configure(foreground="#0a0" if ok else "#a00")
    def bind_submit(self, callback: Callable[[], None]):
        self._submit_cb = callback
        self.submit_btn.configure(command=callback)
    def bind_reset(self, callback: Callable[[], None]):
        self._reset_cb = callback
        self.reset_btn.configure(command=callback)