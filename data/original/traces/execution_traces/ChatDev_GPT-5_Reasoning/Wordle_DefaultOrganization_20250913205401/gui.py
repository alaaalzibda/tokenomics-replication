'''
Optional Tkinter GUI for the Wordle game.
This complements the terminal version; run with: python main.py --gui
'''
import tkinter as tk
from tkinter import messagebox
from typing import List, Tuple, Dict
from game import WordleGame, ABSENT, PRESENT, CORRECT
from words import get_daily_word, get_random_word
# Colors inspired by Wordle
COLOR_BG = "#121213"
COLOR_EMPTY = "#d3d6da"
COLOR_TEXT = "#ffffff"
COLOR_CORRECT = "#6aaa64"
COLOR_PRESENT = "#c9b458"
COLOR_ABSENT = "#787c7e"
QWERTY_LAYOUT = ["QWERTYUIOP", "ASDFGHJKL", "ZXCVBNM"]
class WordleGUI(tk.Tk):
    def __init__(self, date=None, random_word=False):
        super().__init__()
        self.title("Wordle (GUI)")
        self.configure(bg=COLOR_BG)
        # Game setup
        if random_word:
            secret = get_random_word()
        else:
            secret = get_daily_word(date=date)
        self.game = WordleGame(secret_word=secret)
        # UI state
        self.labels: List[List[tk.Label]] = []  # 6x5 grid
        self.keyboard_buttons: Dict[str, tk.Button] = {}
        self._build_board()
        self._build_input()
        self._build_keyboard()
        self.resizable(False, False)
    def _build_board(self):
        board_frame = tk.Frame(self, bg=COLOR_BG)
        board_frame.grid(row=0, column=0, padx=10, pady=10, columnspan=3)
        for r in range(self.game.max_attempts):
            row_labels = []
            for c in range(5):
                lbl = tk.Label(board_frame, text=" ", width=4, height=2, font=("Helvetica", 18, "bold"),
                               bg=COLOR_EMPTY, fg="black", relief="groove", bd=2)
                lbl.grid(row=r, column=c, padx=4, pady=4)
                row_labels.append(lbl)
            self.labels.append(row_labels)
        self.status_label = tk.Label(self, text="Guess the 5-letter word!", bg=COLOR_BG,
                                     fg=COLOR_TEXT, font=("Helvetica", 12))
        self.status_label.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="w")
    def _build_input(self):
        input_frame = tk.Frame(self, bg=COLOR_BG)
        input_frame.grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.entry = tk.Entry(input_frame, width=10, font=("Helvetica", 16))
        self.entry.grid(row=0, column=0, padx=(0, 8))
        self.entry.bind("<Return>", self._on_submit)
        submit_btn = tk.Button(input_frame, text="Submit", command=self._on_submit)
        submit_btn.grid(row=0, column=1)
    def _build_keyboard(self):
        kb_frame = tk.Frame(self, bg=COLOR_BG)
        kb_frame.grid(row=3, column=0, padx=10, pady=(0, 10))
        for r, row in enumerate(QWERTY_LAYOUT):
            row_frame = tk.Frame(kb_frame, bg=COLOR_BG)
            row_frame.grid(row=r, column=0, pady=3)
            for ch in row:
                btn = tk.Button(row_frame, text=ch, width=3, height=1, relief="raised",
                                bg=COLOR_EMPTY, fg="black", state="disabled",
                                font=("Helvetica", 10, "bold"), disabledforeground="black")
                btn.pack(side="left", padx=2)
                self.keyboard_buttons[ch.lower()] = btn
    def _apply_colors_to_row(self, row_idx: int, guess: str, statuses: List[str]):
        for c in range(5):
            lbl = self.labels[row_idx][c]
            ch = guess[c].upper()
            lbl.config(text=ch)
            st = statuses[c]
            if st == CORRECT:
                lbl.config(bg=COLOR_CORRECT, fg="white")
            elif st == PRESENT:
                lbl.config(bg=COLOR_PRESENT, fg="white")
            else:
                lbl.config(bg=COLOR_ABSENT, fg="white")
    def _update_keyboard(self):
        status_map = self.game.get_keyboard_status()
        for ch, btn in self.keyboard_buttons.items():
            st = status_map.get(ch)
            if st == CORRECT:
                btn.config(bg=COLOR_CORRECT, fg="white")
            elif st == PRESENT:
                btn.config(bg=COLOR_PRESENT, fg="white")
            elif st == ABSENT:
                btn.config(bg=COLOR_ABSENT, fg="white")
    def _on_submit(self, event=None):
        guess = self.entry.get().strip()
        ok, msg = self.game.validate_guess(guess)
        if not ok:
            messagebox.showwarning("Invalid guess", msg)
            return
        try:
            statuses = self.game.submit_guess(guess)
        except ValueError as e:
            messagebox.showerror("Error", str(e))
            return
        row_idx = self.game.attempts_used - 1
        self._apply_colors_to_row(row_idx, guess.lower(), statuses)
        self._update_keyboard()
        self.entry.delete(0, tk.END)
        if self.game.is_won:
            self.status_label.config(text=f"Congratulations! You won in {self.game.attempts_used}/6.")
            messagebox.showinfo("You win!", f"You guessed the word: {self.game.secret.upper()}")
            self.entry.config(state="disabled")
        elif self.game.is_over:
            self.status_label.config(text=f"Out of tries. The word was {self.game.secret.upper()}.")
            messagebox.showinfo("Game Over", f"The word was: {self.game.secret.upper()}")
            self.entry.config(state="disabled")
        else:
            self.status_label.config(text=f"Attempts: {self.game.attempts_used}/6")
def run_gui(date=None, random_word: bool = False):
    app = WordleGUI(date=date, random_word=random_word)
    app.mainloop()